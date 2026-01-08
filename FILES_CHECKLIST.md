# Complete Files Checklist

Use this checklist to ensure you have created all necessary files in the correct locations.

## Root Directory Files

- [ ] `requirements.txt` - Python dependencies
- [ ] `README.md` - Project documentation
- [ ] `SETUP_GUIDE.md` - Detailed setup instructions
- [ ] `Procfile` - Railway deployment configuration
- [ ] `railway.json` - Railway build settings
- [ ] `.env.example` - Example environment variables
- [ ] `.gitignore` - Git ignore rules
- [ ] `manage.py` - Django management script

## Django Project Configuration (`invoice_project/`)

- [ ] `__init__.py` - Empty file to make it a Python package
- [ ] `settings.py` - Django settings and configuration
- [ ] `urls.py` - Project-level URL routing
- [ ] `wsgi.py` - WSGI application entry point
- [ ] `asgi.py` - ASGI application entry point

## Core App Root (`core/`)

- [ ] `__init__.py` - Empty file to make it a Python package
- [ ] `models.py` - Database models (BusinessProfile, Client, Invoice, etc.)
- [ ] `views.py` - View functions for handling requests
- [ ] `forms.py` - Form definitions for user input
- [ ] `urls.py` - App-level URL routing
- [ ] `utils.py` - Utility functions (currency conversion, etc.)
- [ ] `admin.py` - Django admin configuration
- [ ] `apps.py` - App configuration

## Core App - Migrations (`core/migrations/`)

- [ ] `__init__.py` - Empty file to make it a Python package
- Note: Migration files will be auto-generated when you run `makemigrations`

## Core App - Templates Base (`core/templates/`)

- [ ] `base.html` - Base template with navigation and structure

## Core App - Registration Templates (`core/templates/registration/`)

- [ ] `login.html` - Login page
- [ ] `register.html` - Registration page with business profile
- [ ] `password_reset.html` - Password reset request page
- [ ] `password_reset_confirm.html` - New password entry page

## Core App - Dashboard Templates (`core/templates/dashboard/`)

- [ ] `index.html` - Main dashboard with statistics and recent invoices
- [ ] `profile.html` - User profile edit page

## Core App - Client Templates (`core/templates/clients/`)

- [ ] `client_list.html` - List all clients
- [ ] `client_form.html` - Create/edit client form
- [ ] `client_detail.html` - View single client with invoices

## Core App - Invoice Templates (`core/templates/invoices/`)

- [ ] `invoice_list.html` - List all invoices with filters
- [ ] `invoice_form.html` - Create/edit invoice with line items
- [ ] `invoice_detail.html` - View invoice details
- [ ] `invoice_confirmation.html` - Success page after creating invoice
- [ ] `invoice_pdf.html` - PDF template for invoice generation

## Core App - Static CSS (`core/static/css/`)

- [ ] `style.css` - Custom CSS styles for the application

## Core App - Static JavaScript (`core/static/js/`)

- [ ] `invoice_calculator.js` - Real-time invoice calculations
- [ ] `ad_tracker.js` - Ad click tracking functionality

## Core App - Static Images (`core/static/img/`)

- [ ] `placeholder-logo.png` - Optional placeholder logo

## Media Directory (`media/`)

- [ ] `logos/` - Directory for uploaded business logos
- Note: This directory will be created automatically when first logo is uploaded

## File Creation Commands

### Create Empty Python Package Files
```bash
# invoice_project package
touch invoice_project/__init__.py
touch invoice_project/asgi.py

# core package
touch core/__init__.py
touch core/migrations/__init__.py
```

### Create Empty Directories
```bash
mkdir -p core/templates/registration
mkdir -p core/templates/dashboard
mkdir -p core/templates/clients
mkdir -p core/templates/invoices
mkdir -p core/static/css
mkdir -p core/static/js
mkdir -p core/static/img
mkdir -p media/logos
```

## File Size Reference

Approximate file sizes to verify you copied correctly:

| File | Lines | Size (KB) |
|------|-------|-----------|
| requirements.txt | 11 | <1 |
| README.md | 450+ | 20-25 |
| settings.py | 130+ | 4-5 |
| models.py | 180+ | 6-7 |
| views.py | 280+ | 10-12 |
| forms.py | 120+ | 4-5 |
| urls.py (core) | 45+ | 2 |
| utils.py | 35+ | 1-2 |
| admin.py | 35+ | 1-2 |
| base.html | 60+ | 2-3 |
| register.html | 150+ | 6-7 |
| login.html | 60+ | 2-3 |
| dashboard/index.html | 180+ | 7-8 |
| invoice_form.html | 180+ | 7-8 |
| invoice_pdf.html | 150+ | 6-7 |
| style.css | 120+ | 3-4 |
| invoice_calculator.js | 45+ | 1-2 |
| ad_tracker.js | 60+ | 2 |

## Verification Steps

### 1. Check File Structure
```bash
tree -I 'venv|__pycache__|*.pyc|staticfiles|*.sqlite3'
```

### 2. Check Python Syntax
```bash
python -m py_compile invoice_project/settings.py
python -m py_compile core/models.py
python -m py_compile core/views.py
python -m py_compile core/forms.py
```

### 3. Check Template Syntax
```bash
python manage.py check
```

### 4. Check Static Files
```bash
python manage.py findstatic css/style.css
python manage.py findstatic js/invoice_calculator.js
```

### 5. Run Django Checks
```bash
python manage.py check --deploy
```

## Common Missing Files

If you get errors, these are commonly missing:

### 1. `__init__.py` files
Create empty `__init__.py` in:
- `invoice_project/`
- `core/`
- `core/migrations/`

### 2. `apps.py` in core
```python
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
```

### 3. `asgi.py` in invoice_project
```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_project.settings')
application = get_asgi_application()
```

### 4. `.env` file
Copy from `.env.example` and fill in your values

## Quick Test After File Creation

```bash
# Check no syntax errors
python manage.py check

# Try making migrations
python manage.py makemigrations

# Try running migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Try running server
python manage.py runserver
```

## File Content Verification

### Verify Key Files Contain:

**settings.py** should have:
- ✅ INSTALLED_APPS with 'core'
- ✅ DATABASES configuration
- ✅ MEDIA_URL and MEDIA_ROOT
- ✅ STATIC settings with WhiteNoise

**models.py** should have:
- ✅ BusinessProfile model
- ✅ Client model
- ✅ Invoice model
- ✅ InvoiceItem model
- ✅ AdClick model

**views.py** should have:
- ✅ register function
- ✅ user_login function
- ✅ dashboard function
- ✅ invoice_create function
- ✅ invoice_pdf function
- ✅ track_ad_click function

**urls.py** (core) should have:
- ✅ All authentication routes
- ✅ All dashboard routes
- ✅ All client routes
- ✅ All invoice routes
- ✅ Ad tracking route

## Next Steps After All Files Created

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure `.env` file
3. ✅ Create database
4. ✅ Run migrations: `python manage.py migrate`
5. ✅ Create superuser: `python manage.py createsuperuser`
6. ✅ Collect static files: `python manage.py collectstatic`
7. ✅ Run server: `python manage.py runserver`
8. ✅ Test application
9. ✅ Commit to Git
10. ✅ Deploy to Railway

## Completed! ✅

When all checkboxes above are checked, your project structure is complete and ready for development!