from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

# Currency choices
CURRENCY_CHOICES = [
    ('USD', 'US Dollar ($)'),
    ('EUR', 'Euro (€)'),
    ('GBP', 'British Pound (£)'),
    ('JPY', 'Japanese Yen (¥)'),
    ('AUD', 'Australian Dollar (A$)'),
    ('CAD', 'Canadian Dollar (C$)'),
    ('CHF', 'Swiss Franc (Fr)'),
    ('CNY', 'Chinese Yuan (¥)'),
    ('INR', 'Indian Rupee (₹)'),
    ('PHP', 'Philippine Peso (₱)'),
]

COUNTRY_CODES = [
    ('+1', 'USA/Canada (+1)'),
    ('+44', 'UK (+44)'),
    ('+63', 'Philippines (+63)'),
    ('+91', 'India (+91)'),
    ('+61', 'Australia (+61)'),
    ('+81', 'Japan (+81)'),
    ('+86', 'China (+86)'),
    ('+33', 'France (+33)'),
    ('+49', 'Germany (+49)'),
]

class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField(max_length=255)
    business_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    business_email = models.EmailField()
    phone_country_code = models.CharField(max_length=5, choices=COUNTRY_CODES, default='+1')
    phone_number = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    zip_postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    preferred_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    created_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} - {self.user.username}"

    class Meta:
        verbose_name = "Business Profile"
        verbose_name_plural = "Business Profiles"


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    zip_postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_invoice_count(self):
        return self.invoices.count()

    class Meta:
        ordering = ['-created_date']
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    pdf_generated = models.BooleanField(default=False)
    
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.filter(user=self.user).order_by('-id').first()
            if last_invoice and last_invoice.invoice_number.startswith('INV-'):
                try:
                    last_number = int(last_invoice.invoice_number.split('-')[1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            self.invoice_number = f"INV-{new_number:05d}"
        
        # Calculate totals
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)

    def is_overdue(self):
        """
        Check if invoice is overdue based on status and due date.
        - Draft invoices are never marked as overdue (just expired)
        - Sent invoices become overdue after due date passes
        - Paid invoices are never overdue
        """
        now = timezone.now()
        
        # Only 'sent' invoices can be overdue
        if self.status == 'sent' and self.due_date < now:
            return True
        return False
    
    def is_expired(self):
        """
        Check if a draft invoice's due date has passed.
        This is different from overdue - drafts just expire, not overdue.
        """
        now = timezone.now()
        if self.status == 'draft' and self.due_date < now:
            return True
        return False
    
    def days_until_due(self):
        """Calculate days until due date (negative if overdue)"""
        now = timezone.now()
        delta = self.due_date - now
        return delta.days
    
    def update_overdue_status(self):
        """
        Update invoice status to overdue if conditions are met.
        This method is called by the scheduled task.
        """
        if self.is_overdue() and self.status == 'sent':
            self.status = 'overdue'
            self.save(update_fields=['status', 'last_modified_timestamp'])
            return True
        return False

    class Meta:
        ordering = ['-created_timestamp']
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_position = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"

    class Meta:
        ordering = ['order_position']
        verbose_name = "Invoice Item"
        verbose_name_plural = "Invoice Items"


class AdClick(models.Model):
    AD_PLACEMENT_CHOICES = [
        ('pdf_download', 'Before PDF Download'),
        ('invoice_sidebar', 'Invoice Creation Sidebar'),
        ('pdf_footer', 'Invoice PDF Footer'),
        ('dashboard_widget', 'Dashboard Widget'),
        ('invoice_confirmation', 'After Invoice Creation'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ad_identifier = models.CharField(max_length=100)
    ad_placement = models.CharField(max_length=30, choices=AD_PLACEMENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    target_url = models.URLField()
    user_context = models.CharField(max_length=255, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.ad_identifier} - {self.ad_placement} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Ad Click"
        verbose_name_plural = "Ad Clicks"