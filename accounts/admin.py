from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FreelancerProfile, ClientProfile, Portfolio, EmailVerification, PasswordReset

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active', 'is_email_verified')
    list_filter = ('user_type', 'is_staff', 'is_active', 'is_email_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'user_type')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_email_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'user_type', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'hourly_rate', 'experience_years', 'wallet_balance')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'wallet_balance')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company_name')

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'freelancer', 'created_at')
    search_fields = ('title', 'freelancer__user__email')

admin.site.register(User, CustomUserAdmin)
admin.site.register(FreelancerProfile, FreelancerProfileAdmin)
admin.site.register(ClientProfile, ClientProfileAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(EmailVerification)
admin.site.register(PasswordReset)
