from django.contrib import admin
from .models import Job, Category

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'budget', 'job_type', 'status', 'created_at')
    list_filter = ('status', 'job_type', 'created_at')
    search_fields = ('title', 'description', 'client__email')
    date_hierarchy = 'created_at'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Job, JobAdmin)
admin.site.register(Category, CategoryAdmin)
