# Project Blog - Django Project

## Overview

This is a Django project created for **Assessment 2** of the HIT237 course (Group 6, 2026). The project is a minimal Django scaffold with no apps yet—providing a clean foundation for future development.

**Project Name:** project_blog  
**Django Version:** 6.0.4  
**Python Version:** 3.12+  
**Database:** SQLite (default)

---

## Installation & Setup

### Prerequisites

- Python 3.12 or later
- pip (Python package manager)
- git (for version control)

### Step 1: Clone or Navigate to Repository

```bash
cd Group6-HIT237-Repository/Assessment\ 2
```

### Step 2: Create Virtual Environment

Create an isolated Python environment for this project:

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs:
- Django 6.0.4
- asgiref 3.11.1
- sqlparse 0.5.5
- tzdata 2026.1

### Step 5: Initialize Database

Run Django migrations to set up the database schema:

```bash
python manage.py migrate
```

This creates the SQLite database (`db.sqlite3`) with default Django tables for authentication, content types, and sessions.

### Step 6: Start Development Server

Launch the development server:

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

Access the server at: **http://127.0.0.1:8000/**

To stop the server, press `Ctrl+C` (or `Ctrl+Break` on Windows).

---

## Project Structure

```
Assessment 2/
├── project_blog/           # Django project configuration
│   ├── __init__.py
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL routing
│   ├── asgi.py             # ASGI configuration
│   └── wsgi.py             # WSGI configuration
├── manage.py               # Django management script
├── db.sqlite3              # SQLite database (created after migrate)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore              # Git exclusions
└── venv/                   # Virtual environment (not committed to git)
```

---

## Management Commands

### Create a New Django App

Once you're ready to add applications:

```bash
python manage.py startapp app_name
```

### Create a Superuser (Admin)

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

Then visit http://127.0.0.1:8000/admin/

### Run Django Shell

Interact with your project via Python REPL:

```bash
python manage.py shell
```

### Check Project Health

Run system checks for any configuration issues:

```bash
python manage.py check
```

---

## Next Steps

1. Create Django apps as needed: `python manage.py startapp app_name`
2. Define models in your apps' `models.py`
3. Create migrations: `python manage.py makemigrations`
4. Apply migrations: `python manage.py migrate`
5. Develop views, templates, and URL routing

---

## Important Notes

- **Do NOT use the development server in production.** Use a production WSGI/ASGI server (e.g., Gunicorn, uWSGI).
- The `venv/` folder is excluded from git (see `.gitignore`). Each developer must create their own virtual environment.
- The `db.sqlite3` file is for development only and is also excluded from git.
- Always activate the virtual environment before working on the project.

---

## Troubleshooting

### Virtual Environment Not Activating

Ensure you're using the correct path and PowerShell execution policy allows scripts to run:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Module Not Found Errors

Make sure the virtual environment is activated and dependencies are installed:

```bash
pip list
```

### Database Errors

Reset the database (dev only):

```bash
rm db.sqlite3
python manage.py migrate
```

---

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/) (for API development)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Last Updated:** April 15, 2026  
**Course:** HIT237 - Assessment 2  
**Group:** 6
