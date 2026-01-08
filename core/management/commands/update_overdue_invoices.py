# core/management/commands/update_overdue_invoices.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Invoice


class Command(BaseCommand):
    help = 'Updates invoice status to overdue for sent invoices past due date'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # Find all 'sent' invoices that are past due date
        overdue_invoices = Invoice.objects.filter(
            status='sent',
            due_date__lt=now
        )
        
        updated_count = 0
        for invoice in overdue_invoices:
            invoice.status = 'overdue'
            invoice.save(update_fields=['status', 'last_modified_timestamp'])
            updated_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated invoice {invoice.invoice_number} to overdue'
                )
            )
        
        if updated_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No invoices to update')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} invoice(s) to overdue'
                )
            )