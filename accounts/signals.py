# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import User, FreelancerProfile, ClientProfile

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         if instance.user_type == 'freelancer':
#             FreelancerProfile.objects.create(user=instance)
#         elif instance.user_type == 'client':
#             ClientProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if instance.user_type == 'freelancer':
#         if hasattr(instance, 'freelancer_profile'):
#             instance.freelancer_profile.save()
#     elif instance.user_type == 'client':
#         if hasattr(instance, 'client_profile'):
#             instance.client_profile.save()