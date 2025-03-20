from django.contrib import admin
from .models import Payment, BankAccount

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'amount', 'payment_type', 'status', 'created_at')
    list_filter = ('payment_type', 'status', 'created_at')
    search_fields = ('sender__email', 'recipient__email', 'job__title')
    date_hierarchy = 'created_at'

class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank_name', 'account_holder_name', 'is_default')
    list_filter = ('is_default', 'bank_name')
    search_fields = ('user__email', 'account_holder_name', 'bank_name')

admin.site.register(Payment, PaymentAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
