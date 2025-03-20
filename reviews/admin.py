from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'reviewer', 'recipient', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__email', 'recipient__email', 'comment')
    date_hierarchy = 'created_at'

admin.site.register(Review, ReviewAdmin)
