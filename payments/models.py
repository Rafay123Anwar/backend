from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job

User = get_user_model()

class Payment(models.Model):
    """Model for payments between clients and freelancers."""
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('job_payment', 'Job Payment'),
        ('deposit', 'Wallet Deposit'),
        ('withdrawal', 'Wallet Withdrawal'),
    )
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_payments')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_payments', null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.payment_type == 'job_payment':
            return f"Payment of ${self.amount} for {self.job.title}"
        elif self.payment_type == 'deposit':
            return f"Deposit of ${self.amount} by {self.sender.email}"
        else:
            return f"Withdrawal of ${self.amount} by {self.sender.email}"

class BankAccount(models.Model):
    """Model for storing bank account information for withdrawals."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    routing_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Bank account for {self.user.email}"
    
    def save(self, *args, **kwargs):
        # If this account is set as default, unset default for all other accounts
        if self.is_default:
            BankAccount.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
