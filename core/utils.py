from decimal import Decimal
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from io import BytesIO
import os

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return Decimal(str(amount))
    FALLBACK_RATES = {'USD': 1.0, 'EUR': 0.92, 'GBP': 0.79, 'JPY': 149.50, 'AUD': 1.53, 'CAD': 1.36, 'CHF': 0.88, 'CNY': 7.24, 'INR': 83.12, 'PHP': 56.50}
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if to_currency in data['rates']:
                return Decimal(str(amount * data['rates'][to_currency]))
    except:
        pass
    try:
        if from_currency in FALLBACK_RATES and to_currency in FALLBACK_RATES:
            amount_in_usd = float(amount) / FALLBACK_RATES[from_currency]
            return Decimal(str(amount_in_usd * FALLBACK_RATES[to_currency]))
    except:
        pass
    return Decimal(str(amount))

CURRENCY_SYMBOLS = {
    'USD': '$', 
    'EUR': '€', 
    'GBP': '£', 
    'JPY': '¥', 
    'AUD': 'A$', 
    'CAD': 'C$', 
    'CHF': 'Fr', 
    'CNY': '¥', 
    'INR': '₹', 
    'PHP': '₱'
}

def get_currency_symbol(currency_code):
    return CURRENCY_SYMBOLS.get(currency_code, currency_code)

def generate_pdf(invoice, user):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=28, textColor=colors.HexColor('#333333'), spaceAfter=20, alignment=TA_RIGHT)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#333333'), spaceAfter=12)
    business = user.business_profile
    
    # Logo handling
    logo_element = None
    if business.business_logo:
        try:
            logo_path = business.business_logo.path
            if os.path.exists(logo_path):
                logo_element = Image(logo_path, width=1.5*inch, height=0.75*inch)
        except:
            pass
    
    # Company info with or without logo
    if logo_element:
        company_info = [[logo_element], [Paragraph(f"<b>{business.business_name}</b>", styles['Normal'])], [Paragraph(f"{business.street_address}<br/>{business.city}, {business.state_province} {business.zip_postal_code}<br/>{business.country}<br/>Email: {business.business_email}<br/>Phone: {business.country_code} {business.phone_number}", styles['Normal'])]]
        company_table = Table(company_info, colWidths=[3.5*inch])
    else:
        company_info = f"<b>{business.business_name}</b><br/>{business.street_address}<br/>{business.city}, {business.state_province} {business.zip_postal_code}<br/>{business.country}<br/>Email: {business.business_email}<br/>Phone: {business.country_code} {business.phone_number}"
        company_table = Paragraph(company_info, styles['Normal'])
    
    invoice_title = Paragraph("INVOICE", title_style)
    invoice_info = f"<b>Invoice #:</b> {invoice.invoice_number}<br/><b>Date:</b> {invoice.invoice_date.strftime('%B %d, %Y')}<br/><b>Due Date:</b> {invoice.due_date.strftime('%B %d, %Y')}<br/><b>Status:</b> {invoice.get_status_display().upper()}"
    
    header_table = Table([[company_table, invoice_title], ['', Paragraph(invoice_info, styles['Normal'])]], colWidths=[3.5*inch, 3.5*inch])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,-1), 'RIGHT')]))
    elements.append(header_table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("BILL TO", heading_style))
    client_info = f"<b>{invoice.client.name}</b><br/>{invoice.client.street_address}<br/>{invoice.client.city}, {invoice.client.state_province} {invoice.client.zip_postal_code}<br/>{invoice.client.country}<br/>Email: {invoice.client.email}<br/>Phone: {invoice.client.phone}"
    client_box = Table([[Paragraph(client_info, styles['Normal'])]], colWidths=[6*inch])
    client_box.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9f9f9')), ('PADDING', (0,0), (-1,-1), 12), ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e0e0e0'))]))
    elements.append(client_box)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("ITEMS", heading_style))
    items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    for item in invoice.items.all():
        items_data.append([item.description, str(item.quantity), f"{invoice.currency} {item.unit_price:.2f}", f"{invoice.currency} {item.line_total:.2f}"])
    
    items_table = Table(items_data, colWidths=[3*inch, 1.2*inch, 1.4*inch, 1.4*inch])
    items_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (1,0), (-1,-1), 'RIGHT'), ('ALIGN', (0,0), (0,-1), 'LEFT'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 12), ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#dddddd')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')]), ('PADDING', (0,1), (-1,-1), 10)]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    totals_data = [['Subtotal:', f"{invoice.currency} {invoice.subtotal:.2f}"], [f'Tax ({invoice.tax_rate}%):', f"{invoice.currency} {invoice.tax_amount:.2f}"]]
    if invoice.discount_amount > 0:
        totals_data.append(['Discount:', f"-{invoice.currency} {invoice.discount_amount:.2f}"])
    totals_data.append(['TOTAL:', f"{invoice.currency} {invoice.total_amount:.2f}"])
    
    totals_table = Table(totals_data, colWidths=[5*inch, 2*inch])
    totals_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'RIGHT'), ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'), ('FONTSIZE', (0,-1), (-1,-1), 14), ('LINEABOVE', (0,-1), (-1,-1), 2, colors.HexColor('#333333')), ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f0f0f0'))]))
    elements.append(totals_table)
    elements.append(Spacer(1, 20))
    
    if invoice.notes:
        elements.append(Paragraph("NOTES", heading_style))
        note_box = Table([[Paragraph(invoice.notes, styles['Normal'])]], colWidths=[6.5*inch])
        note_box.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffef0')), ('PADDING', (0,0), (-1,-1), 12), ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e0e0e0'))]))
        elements.append(note_box)
    
    ad_style = ParagraphStyle('AdStyle', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, textColor=colors.HexColor('#0066cc'))
    ad_box = Table([[Paragraph("Simplify Your Invoicing", ad_style)]], colWidths=[6.5*inch])
    ad_box.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f8ff')), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('PADDING', (0,0), (-1,-1), 15), ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#0066cc'))]))
    elements.append(ad_box)
    
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#666666'))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Thank you! - {business.business_name}", footer_style))
    
    doc.build(elements)
    return buffer.getvalue()
