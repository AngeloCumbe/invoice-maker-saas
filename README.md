# Ad-Integrated Invoice Maker

A comprehensive SaaS web application for creating and managing professional invoices with integrated advertising placements and click tracking.

## Features

### Core Functionality
- ✅ **User Authentication** - Complete registration, login, and password reset
- ✅ **Business Profile Management** - Upload logo, manage company information
- ✅ **Client Management** - Add, edit, delete, and view client details
- ✅ **Invoice Creation** - Create professional invoices with line items
- ✅ **Real-time Calculations** - Automatic subtotal, tax, discount, and total calculations
- ✅ **Multi-Currency Support** - Support for 10+ currencies with conversion
- ✅ **Invoice Status Tracking** - Draft, Sent, and Paid statuses
- ✅ **PDF Generation** - Professional PDF invoices with WeasyPrint
- ✅ **Email Notifications** - Send invoices to clients via email

### Dashboard Features
- 📊 Total clients and invoices count
- 💰 Paid and pending amounts in preferred currency
- 🔄 Currency conversion with hover tooltips
- 📋 Recent invoices table
- 🎯 Quick actions for invoice management

### Advertisement Integration
The application includes **5 strategic ad placements**:

1. **Before PDF Download** - Ad displayed before generating PDF
2. **Invoice Creation Sidebar** - Sidebar ad during invoice creation
3. **Invoice PDF Footer** - Ad embedded in PDF footer
4. **Dashboard Widget** - Prominent ad on dashboard
5. **Invoice Confirmation** - Ad after successful invoice creation

All ad clicks are tracked and stored in the database for analytics.

## Technology Stack

- **Backend**: Django 4.2.7 (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **PDF Generation**: WeasyPrint
- **Currency Conversion**: forex-python
- **Deployment**: Railway.app
- **Version Control**: GitHub

## Database Schema

### 1. Users / Business Profiles
```sql
- user_id (PK)
- username
- email
- password (hashed)
- business_name
- business_logo
- business_email
- phone_country_code
- phone_number
- street_address
- city
- state_province
- zip_postal_code
- country
- preferred_currency
- created_date
- last_login
```

### 2. Clients
```sql
- client_id (PK)
- user_id (FK)
- name
- email
- phone
- street_address
- city
- state_province
- zip_postal_code
- country
- created_date
```

### 3. Invoices
```sql
- invoice_id (PK)
- user_id (FK)
- client_id (FK)
- invoice_number (unique, auto-generated)
- invoice_date
- due_date
- status (draft/sent/paid)
- currency
- subtotal
- tax_rate
- tax_amount
- discount_amount
- total_amount
- notes
- pdf_generated
- created_timestamp
- last_modified_timestamp
```

### 4. Invoice Items
```sql
- item_id (PK)
- invoice_id (FK)
- description
- quantity
- unit_price
- line_total
- order_position
```

### 5. Ad Clicks
```sql
- click_id (PK)
- user_id (FK, nullable)
- session_id
- ad_identifier
- ad_placement
- timestamp
- target_url
- user_context
- invoice_id (FK, nullable)
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ad-integrated-invoice-maker.git
cd ad-integrated-invoice-maker
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**
```bash
# Create database
createdb invoice_db

# Or using psql
psql -U postgres
CREATE DATABASE invoice_db;
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

Required environment variables:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/invoice_db
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

6. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Collect static files**
```bash
python manage.py collectstatic
```

9. **Run development server**
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

## Deployment to Railway.app

### Step 1: Prepare Your Repository
```bash
git init
git add .
git commit -m "Initial commit"
```

### Step 2: Create Railway Project
1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### Step 3: Add PostgreSQL Database
1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a DATABASE_URL

### Step 4: Configure Environment Variables
Add these variables in Railway dashboard:
```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=.railway.app
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Deploy
```bash
git push origin main
```

Railway will automatically:
- Detect your Django app
- Install dependencies from requirements.txt
- Run migrations
- Deploy your application

Your app will be live at `https://your-app.railway.app`

## Usage Guide

### 1. Registration
- Navigate to `/register/`
- Fill in account information (username, email, password)
- Provide business information
- Upload business logo (optional)
- Select preferred currency

### 2. Managing Clients
- Go to **Clients** menu
- Click "Add New Client"
- Enter client details
- View client list with invoice counts

### 3. Creating Invoices
- Go to **Invoices** menu → "Create Invoice"
- Select client from dropdown
- Choose currency and status
- Set due date
- Add line items (description, quantity, unit price)
- Enter tax rate and discount
- Add notes (optional)
- Save invoice

### 4. Invoice Actions
- **View**: See invoice details
- **Edit**: Modify invoice information
- **Download PDF**: Generate and download PDF
- **Delete**: Remove invoice

### 5. Dashboard Overview
- View statistics at a glance
- Monitor paid and pending amounts
- See recent invoices
- Quick access to create new invoices

## Features Walkthrough

### Auto-Generated Invoice Numbers
- Format: `INV-00001`, `INV-00002`, etc.
- Unique per user
- Auto-increments

### Currency Conversion
- Dashboard shows totals in preferred currency
- Hover over paid/pending cards to see breakdown by currency
- Automatic conversion using real-time exchange rates

### Email Notifications
- When invoice status is set to "Sent"
- Automatic email to client with invoice details
- Configurable email settings

### PDF Generation
- Professional invoice layout
- Includes company logo and branding
- Client details and itemized list
- Ad placement in footer
- Downloadable for sharing

### Ad Tracking
- All ad clicks are logged
- Track user engagement
- Analytics data for ad performance
- Context-aware tracking (which page, which invoice)

## Project Structure
```
ad-integrated-invoice-maker/
├── manage.py
├── requirements.txt
├── README.md
├── Procfile
├── railway.json
├── .env.example
├── .gitignore
├── invoice_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                     # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── forms.py             # Form definitions
│   ├── urls.py              # URL routing
│   ├── utils.py             # Utility functions
│   ├── admin.py             # Admin configuration
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── registration/
│   │   ├── dashboard/
│   │   ├── clients/
│   │   └── invoices/
│   └── static/              # Static files
│       ├── css/
│       ├── js/
│       └── img/
└── media/                   # User uploads
    └── logos/
```

## API Endpoints

### Authentication
- `GET/POST /` - Login
- `GET/POST /register/` - User registration
- `GET /logout/` - Logout
- `GET/POST /password-reset/` - Password reset

### Dashboard
- `GET /dashboard/` - Main dashboard
- `GET/POST /profile/` - User profile

### Clients
- `GET /clients/` - List all clients
- `GET/POST /clients/create/` - Create new client
- `GET/POST /clients/<id>/edit/` - Edit client
- `GET /clients/<id>/delete/` - Delete client
- `GET /clients/<id>/` - View client details

### Invoices
- `GET /invoices/` - List all invoices
- `GET/POST /invoices/create/` - Create new invoice
- `GET/POST /invoices/<id>/edit/` - Edit invoice
- `GET /invoices/<id>/delete/` - Delete invoice
- `GET /invoices/<id>/` - View invoice
- `GET /invoices/<id>/pdf/` - Download PDF
- `GET /invoices/<id>/confirmation/` - Confirmation page

### Ad Tracking
- `POST /track-ad/` - Track ad click (AJAX)

## Testing

### Run Tests
```bash
python manage.py test
```

### Create Sample Data
```bash
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth.models import User
from core.models import BusinessProfile, Client, Invoice, InvoiceItem

# Create test user
user = User.objects.create_user('testuser', 'test@example.com', 'password123')

# Create business profile
profile = BusinessProfile.objects.create(
    user=user,
    business_name="Test Company",
    business_email="test@company.com",
    phone_country_code="+1",
    phone_number="1234567890",
    street_address="123 Test St",
    city="Test City",
    state_province="TS",
    zip_postal_code="12345",
    country="Test Country",
    preferred_currency="USD"
)

# Create test client
client = Client.objects.create(
    user=user,
    name="Test Client",
    email="client@example.com",
    phone="+1234567890",
    street_address="456 Client Ave",
    city="Client City",
    state_province="CS",
    zip_postal_code="67890",
    country="Client Country"
)
```

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

**2. Static Files Not Loading**
```bash
python manage.py collectstatic --noinput
```

**3. Email Not Sending**
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- For Gmail, use App Password, not regular password
- Enable "Less secure app access" or use OAuth2

**4. PDF Generation Fails**
```bash
# Install required dependencies
pip install WeasyPrint
# On Ubuntu/Debian
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

## Security Considerations

- ✅ CSRF protection enabled
- ✅ SQL injection protection (ORM)
- ✅ XSS protection
- ✅ Password hashing with Django's PBKDF2
- ✅ HTTPS enforced in production
- ✅ Secure cookie settings
- ✅ Input validation and sanitization

## Performance Optimization

- Database indexing on foreign keys
- Static file compression with WhiteNoise
- Query optimization with select_related()
- Lazy loading for images
- Caching for currency conversion

## Future Enhancements

- [ ] Recurring invoices
- [ ] Payment gateway integration
- [ ] Invoice templates
- [ ] Multi-language support
- [ ] Advanced reporting and analytics
- [ ] Mobile app
- [ ] API for third-party integrations
- [ ] Automated reminders for overdue invoices

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Credits

Developed by [Your Name]
Built with Django and Bootstrap

---

**Note**: Remember to update the `.env` file with your actual credentials before deploying to production. Never commit sensitive information to version control.