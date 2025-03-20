from django.contrib import admin
from .models import Proposal

class ProposalAdmin(admin.ModelAdmin):
    list_display = ('job', 'freelancer', 'bid_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'freelancer__email', 'cover_letter')
    date_hierarchy = 'created_at'

admin.site.register(Proposal, ProposalAdmin)
