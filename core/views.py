from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Q, Count
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import tempfile
import os
from .models import BusinessProfile, Client, Invoice, InvoiceItem, AdClick
from .forms import (UserRegistrationForm, BusinessProfileForm, ClientForm,
                    InvoiceForm, InvoiceItemFormSet)
from .utils import convert_currency, get_currency_symbol

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = BusinessProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if request.POST.get('use_same_email'):
                profile.business_email = user.email
            
            profile.save()
            
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Invoice Maker.')
            return redirect('dashboard')
    else:
        user_form = UserRegistrationForm()
        profile_form = BusinessProfileForm()
    
    return render(request, 'registration/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    try:
        profile = get_object_or_404(BusinessProfile, user=request.user)
        clients = Client.objects.filter(user=request.user)
        invoices = Invoice.objects.filter(user=request.user)
        
        # Update overdue invoices in real-time when dashboard loads
        now = timezone.now()
        overdue_updated = invoices.filter(status='sent', due_date__lt=now)
        for inv in overdue_updated:
            inv.status = 'overdue'
            inv.save(update_fields=['status', 'last_modified_timestamp'])
        
        # Refresh queryset after updates
        invoices = Invoice.objects.filter(user=request.user)
        recent_invoices = invoices.order_by('-created_timestamp')[:5]
        
        # Calculate statistics
        total_clients = clients.count()
        total_invoices = invoices.count()
        overdue_count = invoices.filter(status='overdue').count()
        
        # Calculate paid and pending amounts with currency conversion
        paid_amounts = {}
        pending_amounts = {}
        overdue_amounts = {}
        
        for invoice in invoices:
            if invoice.status == 'paid':
                if invoice.currency not in paid_amounts:
                    paid_amounts[invoice.currency] = Decimal('0')
                paid_amounts[invoice.currency] += invoice.total_amount
            elif invoice.status == 'overdue':
                if invoice.currency not in overdue_amounts:
                    overdue_amounts[invoice.currency] = Decimal('0')
                overdue_amounts[invoice.currency] += invoice.total_amount
            else:
                if invoice.currency not in pending_amounts:
                    pending_amounts[invoice.currency] = Decimal('0')
                pending_amounts[invoice.currency] += invoice.total_amount
        
        # Calculate totals in preferred currency
        total_paid = Decimal('0')
        for currency, amount in paid_amounts.items():
            try:
                converted = convert_currency(float(amount), currency, profile.preferred_currency)
                total_paid += converted
            except Exception as e:
                print(f"Error converting {currency} to {profile.preferred_currency}: {e}")
                total_paid += amount
        
        total_pending = Decimal('0')
        for currency, amount in pending_amounts.items():
            try:
                converted = convert_currency(float(amount), currency, profile.preferred_currency)
                total_pending += converted
            except Exception as e:
                print(f"Error converting {currency} to {profile.preferred_currency}: {e}")
                total_pending += amount
        
        total_overdue = Decimal('0')
        for currency, amount in overdue_amounts.items():
            try:
                converted = convert_currency(float(amount), currency, profile.preferred_currency)
                total_overdue += converted
            except Exception as e:
                print(f"Error converting {currency} to {profile.preferred_currency}: {e}")
                total_overdue += amount
        
        context = {
            'profile': profile,
            'total_clients': total_clients,
            'total_invoices': total_invoices,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'total_overdue': total_overdue,
            'overdue_count': overdue_count,
            'paid_amounts': paid_amounts,
            'pending_amounts': pending_amounts,
            'overdue_amounts': overdue_amounts,
            'recent_invoices': recent_invoices,
            'currency_symbol': get_currency_symbol(profile.preferred_currency),
        }
        
        return render(request, 'dashboard/index.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'dashboard/index.html', {
            'profile': None,
            'total_clients': 0,
            'total_invoices': 0,
            'total_paid': 0,
            'total_pending': 0,
            'total_overdue': 0,
            'overdue_count': 0,
            'paid_amounts': {},
            'pending_amounts': {},
            'overdue_amounts': {},
            'recent_invoices': [],
            'currency_symbol': '$',
        })


@login_required
def profile_view(request):
    profile = get_object_or_404(BusinessProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = BusinessProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = BusinessProfileForm(instance=profile)
    
    return render(request, 'dashboard/profile.html', {
        'profile': profile,
        'profile_form': profile_form
    })


@login_required
def client_list(request):
    clients = Client.objects.filter(user=request.user).annotate(
        invoice_count=Count('invoices')
    )
    return render(request, 'clients/client_list.html', {'clients': clients})


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            messages.success(request, f'Client "{client.name}" created successfully!')
            return redirect('client_list')
    else:
        form = ClientForm()
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'title': 'Add New Client'
    })


@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client "{client.name}" updated successfully!')
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'title': 'Edit Client',
        'client': client
    })


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk, user=request.user)
    client_name = client.name
    client.delete()
    messages.success(request, f'Client "{client_name}" deleted successfully!')
    return redirect('client_list')


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk, user=request.user)
    invoices = Invoice.objects.filter(client=client)
    
    return render(request, 'clients/client_detail.html', {
        'client': client,
        'invoices': invoices
    })


@login_required
def invoice_list(request):
    invoices = Invoice.objects.filter(user=request.user)
    
    # Update overdue invoices in real-time
    now = timezone.now()
    overdue_to_update = invoices.filter(status='sent', due_date__lt=now)
    for inv in overdue_to_update:
        inv.status = 'overdue'
        inv.save(update_fields=['status', 'last_modified_timestamp'])
    
    # Refresh queryset
    invoices = Invoice.objects.filter(user=request.user)
    
    # Count by status
    draft_count = invoices.filter(status='draft').count()
    sent_count = invoices.filter(status='sent').count()
    paid_count = invoices.filter(status='paid').count()
    overdue_count = invoices.filter(status='overdue').count()
    
    return render(request, 'invoices/invoice_list.html', {
        'invoices': invoices,
        'draft_count': draft_count,
        'sent_count': sent_count,
        'paid_count': paid_count,
        'overdue_count': overdue_count,
    })


@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, user=request.user)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            
            # Calculate subtotal from items
            subtotal = Decimal('0')
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                    qty = item_form.cleaned_data.get('quantity', 0)
                    price = item_form.cleaned_data.get('unit_price', 0)
                    subtotal += qty * price
            
            invoice.subtotal = subtotal
            invoice.save()
            
            # Save items
            formset.instance = invoice
            for i, item_form in enumerate(formset):
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                    item = item_form.save(commit=False)
                    item.invoice = invoice
                    item.order_position = i
                    item.save()
            
            # Send email if status is "sent"
            if invoice.status == 'sent':
                try:
                    send_invoice_email(invoice)
                    messages.success(request, f'Invoice {invoice.invoice_number} created and email sent to {invoice.client.email}!')
                except Exception as e:
                    messages.warning(request, f'Invoice created but email failed to send: {str(e)}')
            else:
                messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
            
            return redirect('invoice_confirmation', pk=invoice.pk)
    else:
        form = InvoiceForm(user=request.user)
        formset = InvoiceItemFormSet(queryset=InvoiceItem.objects.none())
    
    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice'
    })

@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    old_status = invoice.status  # Track the old status
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice, user=request.user)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            # Calculate subtotal
            subtotal = Decimal('0')
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                    qty = item_form.cleaned_data.get('quantity', 0)
                    price = item_form.cleaned_data.get('unit_price', 0)
                    subtotal += qty * price
            
            invoice = form.save(commit=False)
            invoice.subtotal = subtotal
            new_status = invoice.status  # Get the new status
            invoice.save()
            
            formset.save()
            
            # Send email ONLY if status CHANGED to "sent"
            if old_status != 'sent' and new_status == 'sent':
                try:
                    send_invoice_email(invoice)
                    messages.success(request, f'Invoice {invoice.invoice_number} updated and email sent to {invoice.client.email}!')
                except Exception as e:
                    messages.warning(request, f'Invoice updated but email failed to send: {str(e)}')
            else:
                messages.success(request, f'Invoice {invoice.invoice_number} updated successfully!')
            
            return redirect('invoice_confirmation', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice, user=request.user)
        formset = InvoiceItemFormSet(instance=invoice)
    
    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Invoice',
        'invoice': invoice
    })


@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    invoice_number = invoice.invoice_number
    invoice.delete()
    messages.success(request, f'Invoice {invoice_number} deleted successfully!')
    return redirect('invoice_list')


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    profile = get_object_or_404(BusinessProfile, user=request.user)
    
    # Check if invoice should be overdue
    if invoice.is_overdue():
        invoice.status = 'overdue'
        invoice.save(update_fields=['status', 'last_modified_timestamp'])
    
    return render(request, 'invoices/invoice_detail.html', {
        'invoice': invoice,
        'profile': profile
    })


@login_required
def invoice_confirmation(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    is_new = 'edit' not in request.path
    
    return render(request, 'invoices/invoice_confirmation.html', {
        'invoice': invoice,
        'is_new': is_new
    })


@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    profile = get_object_or_404(BusinessProfile, user=request.user)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice-{invoice.invoice_number}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter, 
                           topMargin=0.3*inch, 
                           bottomMargin=0.75*inch,
                           leftMargin=0.75*inch,
                           rightMargin=0.75*inch)
    elements = []
    styles = getSampleStyleSheet()
    currency_symbol = get_currency_symbol(invoice.currency)
    
    # ==================== HEADER ====================
    # Left side - Company info
    left_content = []
    
    # Add logo if exists
    if profile.business_logo:
        try:
            logo_path = os.path.join(settings.MEDIA_ROOT, str(profile.business_logo))
            if os.path.exists(logo_path):
                img = Image(logo_path)
                img_width, img_height = img.imageWidth, img.imageHeight
                max_width = 150
                max_height = 80
                aspect = img_height / float(img_width)
                
                if img_width > max_width:
                    img_width = max_width
                    img_height = img_width * aspect
                if img_height > max_height:
                    img_height = max_height
                    img_width = img_height / aspect
                
                img.drawWidth = img_width
                img.drawHeight = img_height
                left_content.append(img)
                left_content.append(Spacer(1, 0.1*inch))
        except Exception as e:
            print(f"Error loading logo: {e}")
    
    company_style = ParagraphStyle('Company', parent=styles['Normal'], fontSize=11, leading=14)
    
    left_content.append(Paragraph(f"<b>{profile.business_name}</b>", company_style))
    left_content.append(Paragraph(profile.street_address, company_style))
    left_content.append(Paragraph(f"{profile.city}, {profile.state_province} {profile.zip_postal_code}", company_style))
    left_content.append(Paragraph(profile.country, company_style))
    left_content.append(Paragraph(f"Email: {profile.business_email}", company_style))
    left_content.append(Paragraph(f"Phone: {profile.phone_country_code} {profile.phone_number}", company_style))
    
    # Right side - Invoice title and info
    right_content = []
    
    invoice_title_style = ParagraphStyle('InvoiceTitle', parent=styles['Heading1'], 
                                        fontSize=28, fontName='Helvetica-Bold',
                                        textColor=colors.HexColor('#333333'),
                                        alignment=TA_RIGHT, spaceAfter=10)
    
    invoice_info_style = ParagraphStyle('InvoiceInfo', parent=styles['Normal'],
                                       fontSize=11, leading=14, alignment=TA_RIGHT)
    
    right_content.append(Paragraph("INVOICE", invoice_title_style))
    right_content.append(Paragraph(f"<b>Invoice #:</b> {invoice.invoice_number}", invoice_info_style))
    right_content.append(Paragraph(f"<b>Date:</b> {invoice.invoice_date.strftime('%B %d, %Y')}", invoice_info_style))
    right_content.append(Paragraph(f"<b>Due Date:</b> {invoice.due_date.strftime('%B %d, %Y')}", invoice_info_style))
    right_content.append(Paragraph(f"<b>Status:</b> {invoice.get_status_display().upper()}", invoice_info_style))
    
    # Header table
    header_data = [[left_content, right_content]]
    header_table = Table(header_data, colWidths=[3.25*inch, 3.25*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # ==================== BILL TO ====================
    bill_to_style = ParagraphStyle('BillTo', parent=styles['Heading2'], 
                                   fontSize=12, fontName='Helvetica-Bold')
    client_style = ParagraphStyle('Client', parent=styles['Normal'], fontSize=11, leading=14)
    
    elements.append(Paragraph("Bill To:", bill_to_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"<b>{invoice.client.name}</b>", client_style))
    elements.append(Paragraph(invoice.client.street_address, client_style))
    elements.append(Paragraph(f"{invoice.client.city}, {invoice.client.state_province} {invoice.client.zip_postal_code}", client_style))
    elements.append(Paragraph(invoice.client.country, client_style))
    elements.append(Paragraph(f"Email: {invoice.client.email}", client_style))
    elements.append(Paragraph(f"Phone: {invoice.client.phone}", client_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # ==================== LINE ITEMS TABLE ====================
    items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    
    for item in invoice.items.all():
        items_data.append([
            item.description,
            str(item.quantity),
            "{0}{1}".format(currency_symbol, item.unit_price),
            "{0}{1}".format(currency_symbol, item.line_total)
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.25*inch, 1.25*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # ==================== TOTALS SECTION ====================
    # Create plain text strings WITHOUT any HTML tags
    subtotal_value = "{0}{1}".format(currency_symbol, invoice.subtotal)
    tax_value = "{0}{1}".format(currency_symbol, invoice.tax_amount)
    discount_value = "{0}{1}".format(currency_symbol, invoice.discount_amount)
    total_value = "{0}{1}".format(currency_symbol, invoice.total_amount)
    
    # Regular totals
    totals_data = [
        ['Subtotal:', subtotal_value],
        ['Tax ({0}%):'.format(invoice.tax_rate), tax_value],
        ['Discount:', discount_value],
    ]
    
    totals_table = Table(totals_data, colWidths=[4.5*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)
    
    # Total row - separate table with bold styling
    total_data = [['Total:', total_value]]
    
    total_table = Table(total_data, colWidths=[4.5*inch, 2*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(total_table)
    
    # ==================== NOTES ====================
    if invoice.notes:
        elements.append(Spacer(1, 0.4*inch))
        
        notes_heading_style = ParagraphStyle('NotesHeading', parent=styles['Heading2'],
                                            fontSize=12, fontName='Helvetica-Bold')
        notes_text_style = ParagraphStyle('NotesText', parent=styles['Normal'],
                                         fontSize=10, leading=14)
        
        elements.append(Paragraph("Notes:", notes_heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        notes_data = [[Paragraph(invoice.notes, notes_text_style)]]
        notes_table = Table(notes_data, colWidths=[6.5*inch])
        notes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (0, 0), (-1, 0), 4, colors.HexColor('#007bff')),
        ]))
        elements.append(notes_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # ==================== FOOTER ====================
    elements.append(Spacer(1, 0.5*inch))
    
    footer_text_style = ParagraphStyle('FooterText', parent=styles['Normal'],
                                      fontSize=9, alignment=TA_CENTER, leading=12)
    
    footer_ad = "💼 Simplify Your Business - Try our complete accounting suite at www.example.com/accounting"
    footer_data = [[Paragraph(footer_ad, footer_text_style)]]
    
    footer_table = Table(footer_data, colWidths=[6.5*inch])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff3cd')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#ffc107')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(footer_table)
    
    elements.append(Spacer(1, 0.1*inch))
    
    business_footer = "Thank you for your business! | {0} | {1}".format(
        profile.business_name, profile.business_email)
    business_footer_style = ParagraphStyle('BusinessFooter', parent=styles['Normal'],
                                          fontSize=8, alignment=TA_CENTER,
                                          textColor=colors.HexColor('#666666'))
    elements.append(Paragraph(business_footer, business_footer_style))
    
    # ==================== BUILD ====================
    doc.build(elements)
    
    invoice.pdf_generated = True
    invoice.save()
    
    return response


@login_required
def track_ad_click(request):
    if request.method == 'POST':
        ad_id = request.POST.get('ad_id')
        placement = request.POST.get('placement')
        target_url = request.POST.get('target_url')
        context = request.POST.get('context', '')
        invoice_id = request.POST.get('invoice_id')
        
        ad_click = AdClick.objects.create(
            user=request.user,
            session_id=request.session.session_key,
            ad_identifier=ad_id,
            ad_placement=placement,
            target_url=target_url,
            user_context=context,
            invoice_id=invoice_id if invoice_id else None
        )
        
        return JsonResponse({'success': True, 'click_id': ad_click.id})
    
    return JsonResponse({'success': False}, status=400)


def send_invoice_email(invoice):
    """Send invoice to client via email"""
    subject = f'Invoice {invoice.invoice_number} from {invoice.user.business_profile.business_name}'
    message = f"""
    Dear {invoice.client.name},
    
    Please find attached your invoice {invoice.invoice_number}.
    
    Invoice Details:
    - Invoice Number: {invoice.invoice_number}
    - Date: {invoice.invoice_date.strftime('%B %d, %Y')}
    - Due Date: {invoice.due_date.strftime('%B %d, %Y')}
    - Total Amount: {get_currency_symbol(invoice.currency)}{invoice.total_amount}
    
    Thank you for your business!
    
    Best regards,
    {invoice.user.business_profile.business_name}
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [invoice.client.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f"Error sending email: {e}")