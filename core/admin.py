from django.contrib import admin
from django.utils import timezone
from .models import BusinessProfile, Client, Invoice, InvoiceItem, AdClick

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'business_email', 'preferred_currency', 'created_date']
    search_fields = ['business_name', 'user__username', 'business_email']
    list_filter = ['preferred_currency', 'created_date']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'user', 'created_date']
    search_fields = ['name', 'email', 'user__username']
    list_filter = ['created_date', 'country']

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class OverdueFilter(admin.SimpleListFilter):
    title = 'overdue status'
    parameter_name = 'overdue'

    def lookups(self, request, model_admin):
        return (
            ('overdue', 'Overdue'),
            ('due_soon', 'Due Soon (3 days)'),
            ('expired_draft', 'Expired Draft'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'overdue':
            return queryset.filter(status='overdue')
        if self.value() == 'due_soon':
            three_days = now + timezone.timedelta(days=3)
            return queryset.filter(status='sent', due_date__lte=three_days, due_date__gte=now)
        if self.value() == 'expired_draft':
            return queryset.filter(status='draft', due_date__lt=now)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'user', 'status', 'total_amount', 'currency', 'invoice_date', 'due_date', 'is_overdue_display']
    search_fields = ['invoice_number', 'client__name', 'user__username']
    list_filter = ['status', 'currency', 'invoice_date', OverdueFilter]
    inlines = [InvoiceItemInline]
    readonly_fields = ['invoice_number', 'subtotal', 'tax_amount', 'total_amount', 'created_timestamp', 'last_modified_timestamp']
    
    def is_overdue_display(self, obj):
        if obj.is_overdue():
            return '⚠️ Yes'
        elif obj.is_expired():
            return '⏰ Expired'
        return '✓ No'
    is_overdue_display.short_description = 'Overdue'
    
    actions = ['mark_as_paid', 'mark_as_sent', 'update_overdue_status']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} invoice(s) marked as paid.')
    mark_as_paid.short_description = 'Mark selected invoices as paid'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='sent')
        self.message_user(request, f'{updated} invoice(s) marked as sent.')
    mark_as_sent.short_description = 'Mark selected invoices as sent'
    
    def update_overdue_status(self, request, queryset):
        now = timezone.now()
        updated = 0
        for invoice in queryset.filter(status='sent', due_date__lt=now):
            invoice.status = 'overdue'
            invoice.save()
            updated += 1
        self.message_user(request, f'{updated} invoice(s) updated to overdue.')
    update_overdue_status.short_description = 'Update overdue status'

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'invoice', 'quantity', 'unit_price', 'line_total']
    search_fields = ['description', 'invoice__invoice_number']

@admin.register(AdClick)
class AdClickAdmin(admin.ModelAdmin):
    list_display = ['ad_identifier', 'ad_placement', 'user', 'timestamp', 'target_url']
    search_fields = ['ad_identifier', 'user__username', 'target_url']
    list_filter = ['ad_placement', 'timestamp']