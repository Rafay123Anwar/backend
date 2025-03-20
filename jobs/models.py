from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    """Model for job categories."""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Job(models.Model):
    """Model for job postings."""
    JOB_STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    JOB_TYPE_CHOICES = (
        ('fixed', 'Fixed Price'),
        ('hourly', 'Hourly Rate'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='jobs')
    skills_required = models.JSONField(default=list)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    job_type = models.CharField(max_length=10, choices=JOB_TYPE_CHOICES, default='fixed')
    status = models.CharField(max_length=15, choices=JOB_STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
