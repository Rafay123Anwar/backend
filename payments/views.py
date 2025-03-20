import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment, BankAccount
from .serializers import PaymentSerializer, BankAccountSerializer
from accounts.models import FreelancerProfile, ClientProfile
from jobs.models import Job

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(sender=user) | Payment.objects.filter(recipient=user)
    
    def get_permissions(self):
        if self.action in ['create', 'deposit', 'job_payment', 'withdrawal']:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['post'])
    def deposit(self, request):
        """Add funds to client wallet."""
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create Stripe payment intent
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                metadata={'user_id': request.user.id, 'payment_type': 'deposit'}
            )
            
            # Create payment record
            payment = Payment.objects.create(
                sender=request.user,
                amount=amount,
                payment_type='deposit',
                status='pending',
                stripe_payment_id=payment_intent.id
            )
            
            return Response({
                'payment_id': payment.id,
                'client_secret': payment_intent.client_secret
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def job_payment(self, request):
        """Client pays freelancer for a job."""
        job_id = request.data.get('job_id')
        amount = request.data.get('amount')
        
        if not job_id or not amount:
            return Response({'error': 'Job ID and amount are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the job and check if the user is the client
        try:
            job = Job.objects.get(id=job_id)
            if job.client != request.user:
                return Response({'error': 'You are not the client of this job'}, status=status.HTTP_403_FORBIDDEN)
            
            # Get the freelancer from the accepted proposal
            accepted_proposal = job.proposals.filter(status='accepted').first()
            if not accepted_proposal:
                return Response({'error': 'No accepted proposal found for this job'}, status=status.HTTP_400_BAD_REQUEST)
            
            freelancer = accepted_proposal.freelancer
            
            # Check if client has enough balance
            client_profile = ClientProfile.objects.get(user=request.user)
            if client_profile.wallet_balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create payment record
            payment = Payment.objects.create(
                sender=request.user,
                recipient=freelancer,
                job=job,
                amount=amount,
                payment_type='job_payment',
                status='completed'
            )
            
            # Update wallet balances
            client_profile.wallet_balance -= amount
            client_profile.save()
            
            freelancer_profile = FreelancerProfile.objects.get(user=freelancer)
            freelancer_profile.wallet_balance += amount
            freelancer_profile.save()
            
            # Create notification for the freelancer
            from notifications.models import Notification
            Notification.objects.create(
                recipient=freelancer,
                sender=request.user,
                notification_type='payment_received',
                content=f'You received a payment of ${amount} for "{job.title}"',
                related_job=job
            )
            
            return Response({
                'payment_id': payment.id,
                'status': 'completed',
                'message': f'Payment of ${amount} sent to {freelancer.email}'
            })
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def withdrawal(self, request):
        """Freelancer withdraws funds from wallet."""
        amount = request.data.get('amount')
        bank_account_id = request.data.get('bank_account_id')
        
        if not amount or not bank_account_id:
            return Response({'error': 'Amount and bank account ID are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the user is a freelancer
        if request.user.user_type != 'freelancer':
            return Response({'error': 'Only freelancers can withdraw funds'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the bank account belongs to the user
        try:
            bank_account = BankAccount.objects.get(id=bank_account_id, user=request.user)
        except BankAccount.DoesNotExist:
            return Response({'error': 'Bank account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if freelancer has enough balance
        freelancer_profile = FreelancerProfile.objects.get(user=request.user)
        if freelancer_profile.wallet_balance < amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment record
        payment = Payment.objects.create(
            sender=request.user,
            amount=amount,
            payment_type='withdrawal',
            status='pending'
        )
        
        # In a real application, you would initiate a bank transfer here
        # For this example, we'll just update the status to completed
        payment.status = 'completed'
        payment.save()
        
        # Update wallet balance
        freelancer_profile.wallet_balance -= amount
        freelancer_profile.save()
        
        return Response({
            'payment_id': payment.id,
            'status': 'completed',
            'message': f'Withdrawal of ${amount} initiated to your bank account'
        })
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Check payment status."""
        payment = self.get_object()
        
        # If it's a Stripe payment, check the status from Stripe
        if payment.stripe_payment_id and payment.status == 'pending':
            try:
                payment_intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_id)
                
                if payment_intent.status == 'succeeded':
                    payment.status = 'completed'
                    payment.save()
                    
                    # Update wallet balance for deposits
                    if payment.payment_type == 'deposit':
                        client_profile = ClientProfile.objects.get(user=payment.sender)
                        client_profile.wallet_balance += payment.amount
                        client_profile.save()
                
                return Response({
                    'payment_id': payment.id,
                    'stripe_status': payment_intent.status,
                    'status': payment.status
                })
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'payment_id': payment.id,
            'status': payment.status
        })

class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = BankAccountSerializer
    
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        bank_account = self.get_object()
        bank_account.is_default = True
        bank_account.save()
        return Response({'status': 'default bank account set'})
