# Complete Setup Guide - Ad-Integrated Invoice Maker

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] PostgreSQL installed and running
- [ ] Git installed
- [ ] Text editor/IDE ready
- [ ] Railway.app account (for deployment)
- [ ] Gmail account with App Password (for emails)

## Part 1: Local Development Setup

### Step 1: Install Python and Dependencies

**Windows:**
```bash
# Download Python from python.org
# During installation, check "Add Python to PATH"

# Verify installation
python --version
pip --version
```

**Mac/Linux:**
```bash
# Python usually pre-installed, verify:
python3 --version
pip3 --version
```

### Step 2: Install PostgreSQL

**Windows:**
1. Download from https://www.postgresql.org/download/windows/
2. Run installer, remember your password
3. Default port: 5432

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 3: Create Project Directory

```bash
mkdir invoice-maker
cd invoice-maker
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# You should see (venv) in your terminal
```

### Step 5: Create Project Files

Create all the files as shown in the project structure. You can copy each file content from the artifacts provided.

**Project structure:**
```
invoice-maker/
├── manage.py
├── requirements.txt
├── README.md
├── Procfile
├── railway.json
├── .env.example
├── .gitignore
├── invoice_project/
│   ├── __init__.py (empty file)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py (empty file)
└── core/
    ├── __init__.py (empty file)
    ├── models.py
    ├── views.py
    ├── forms.py
    ├── urls.py
    ├── utils.py
    ├── admin.py
    ├── apps.py (create this)
    ├── migrations/
    │   └── __init__.py (empty file)
    ├── templates/
    │   └── (all HTML files)
    └── static/
        └── (all CSS/JS files)
```

### Step 6: Create `core/apps.py`

```python
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
```

### Step 7: Create `invoice_project/asgi.py`

```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_project.settings')
application = get_asgi_application()
```

### Step 8: Install Dependencies

```bash
pip install -r requirements.txt
```

If you get errors, install individually:
```bash
pip install Django==4.2.7
pip install psycopg2-binary
pip install python-dotenv
pip install Pillow
pip install WeasyPrint
pip install gunicorn
pip install whitenoise
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install forex-python
pip install dj-database-url
```

### Step 9: Create PostgreSQL Database

```bash
# Open PostgreSQL
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE invoice_db;
CREATE USER invoice_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE invoice_db TO invoice_user;
\q
```

### Step 10: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your settings
```

**Edit `.env`:**
```
SECRET_KEY=your-secret-key-generate-using-python
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://invoice_user:your_password@localhost:5432/invoice_db
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 11: Setup Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate password for "Mail"
5. Copy the 16-character password
6. Put it in your .env file as EMAIL_HOST_PASSWORD

### Step 12: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 13: Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### Step 14: Create Static Files Directory

```bash
python manage.py collectstatic --noinput
```

### Step 15: Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 🎉

### Step 16: Test the Application

1. Register a new account at `/register/`
2. Create a client
3. Create an invoice
4. Download PDF
5. Check admin panel at `/admin/`

## Part 2: GitHub Setup

### Step 1: Initialize Git

```bash
git init
git add .
git commit -m "Initial commit: Invoice Maker SaaS"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com
2. Click "New Repository"
3. Name: `ad-integrated-invoice-maker`
4. Keep it private or public
5. Don't initialize with README (we have one)
6. Click "Create repository"

### Step 3: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/ad-integrated-invoice-maker.git
git branch -M main
git push -u origin main
```

## Part 3: Railway.app Deployment

### Step 1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub
3. Verify your email

### Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select your invoice-maker repository

### Step 3: Add PostgreSQL Database

1. In your project, click "New"
2. Select "Database"
3. Choose "Add PostgreSQL"
4. Railway automatically creates DATABASE_URL

### Step 4: Configure Environment Variables

In Railway dashboard, go to Variables tab:

```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=.railway.app
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### Step 5: Deploy

Railway will automatically:
1. Detect your Django app
2. Install requirements
3. Run migrations (from Procfile)
4. Start gunicorn server

### Step 6: Get Your URL

1. Go to Settings tab
2. Under Domains, click "Generate Domain"
3. Your app will be at: `https://your-app.railway.app`

### Step 7: Create Superuser on Production

```bash
# In Railway dashboard, go to your service
# Click on "Deploy Logs"
# Use the Railway CLI or run:

# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Run command
railway run python manage.py createsuperuser
```

## Part 4: Testing & Verification

### Local Testing Checklist

- [ ] Can register new account
- [ ] Can login/logout
- [ ] Can create business profile
- [ ] Can add clients
- [ ] Can create invoices
- [ ] Line items calculate correctly
- [ ] Tax and discount calculate correctly
- [ ] Can edit invoices
- [ ] Can download PDF
- [ ] PDF looks professional
- [ ] Ads display correctly
- [ ] Ad clicks are tracked
- [ ] Dashboard shows correct stats
- [ ] Currency conversion works
- [ ] Email functionality works

### Production Testing

- [ ] App loads at Railway URL
- [ ] HTTPS is enabled
- [ ] Can register and login
- [ ] All features work
- [ ] Static files load correctly
- [ ] Media files upload correctly
- [ ] Database persists data
- [ ] Email sending works

## Part 5: Common Issues & Solutions

### Issue 1: ModuleNotFoundError

```bash
# Solution: Install missing module
pip install <module-name>
# Or reinstall all
pip install -r requirements.txt
```

### Issue 2: Database Connection Error

```bash
# Check PostgreSQL is running
# Windows:
net start postgresql-x64-14
# Mac:
brew services start postgresql
# Linux:
sudo systemctl start postgresql

# Verify DATABASE_URL in .env
```

### Issue 3: Static Files Not Loading

```bash
python manage.py collectstatic --noinput
# Make sure STATIC_ROOT is set in settings.py
```

### Issue 4: WeasyPrint Installation Error

**Windows:**
```bash
# Install GTK3 first
# Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
pip install WeasyPrint
```

**Mac:**
```bash
brew install cairo pango gdk-pixbuf libffi
pip install WeasyPrint
```

**Linux:**
```bash
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
pip install WeasyPrint
```

### Issue 5: Email Not Sending

```
Check:
1. Gmail App Password (not regular password)
2. 2-Step Verification enabled
3. EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
4. EMAIL_USE_TLS=True
```

### Issue 6: Railway Deployment Fails

```
Check:
1. requirements.txt has all dependencies
2. Procfile is correct
3. railway.json is present
4. Environment variables are set
5. Database is connected
```

## Part 6: Maintenance

### Backup Database

```bash
# Local backup
pg_dump invoice_db > backup.sql

# Restore
psql invoice_db < backup.sql
```

### Update Dependencies

```bash
pip install --upgrade django
pip freeze > requirements.txt
```

### Monitor Logs

```bash
# Railway CLI
railway logs

# Django debug
python manage.py runserver --verbosity 2
```

## Part 7: Next Steps

### Enhance Features
- Add invoice templates
- Add payment gateway integration
- Add recurring invoices
- Add client portal
- Add multi-user support
- Add API endpoints

### Optimize Performance
- Enable caching
- Optimize database queries
- Compress images
- Implement CDN for static files

### Security Hardening
- Enable HTTPS redirect
- Add rate limiting
- Implement CORS
- Add security headers
- Regular security audits

## Support

If you encounter issues:

1. Check error messages in terminal
2. Review Django documentation
3. Check Railway logs
4. Google specific error messages
5. Ask on Stack Overflow with proper tags

## Congratulations! 🎉

You now have a fully functional Invoice Maker SaaS application deployed and running!

**Next:** Start using it for your business or customize it further based on your needs.