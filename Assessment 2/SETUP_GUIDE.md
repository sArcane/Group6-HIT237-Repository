# Setup Guide for Local Development

## Prerequisites
- Python 3.10 or higher installed
- Git installed
- A code editor (VS Code, PyCharm, etc.)

## Installation Steps

### 1. Clone and Navigate to Project

```bash
# Clone the repository (replace YOUR-USERNAME and BRANCH-NAME with actual values)
git clone https://github.com/YOUR-USERNAME/Group6-HIT237-Repository.git

# Navigate to the cloned folder
cd Group6-HIT237-Repository

# Navigate to Assessment 2 folder
cd "Assessment 2"
```

**Note:** Replace `YOUR-USERNAME` with your actual GitHub username and `BRANCH-NAME` with the branch you created.

### 2. Create Virtual Environment

**On Windows (PowerShell or Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal line.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Django and all required packages.

### 4. Create Media Directory (for audio uploads)

**On Windows:**
```bash
mkdir media
```

**On macOS/Linux:**
```bash
mkdir -p media
```

### 5. Setup Database

```bash
python manage.py migrate
```

This creates a new `db.sqlite3` file with all the database tables. This file is NOT in GitHub (it's .gitignore'd).

### 6. Create Admin User (Recommended)

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: (any username, e.g., "admin")
- Email: (your email, e.g., "admin@test.com")  
- Password: (make it memorable for testing)
- Confirm password

### 7. Add Test Data (Species & Locations)

You MUST add these before using the form:

1. Start the server:
```bash
python manage.py runserver
```

2. Go to: http://localhost:8000/admin/
3. Log in with your admin credentials from step 6
4. Click "Species" → Add a few species:
   - Name: "Kookaburra"
   - Scientific name: "Dacelo novaeguineae"
   - Conservation status: (choose one)
   - Click Save & Continue
   
5. Click "Locations" → Add a few locations:
   - Name: "Melbourne"
   - Click Save
   - Repeat for "Sydney", "Brisbane", etc.

### 8. Start the Development Server

```bash
python manage.py runserver
```

Open your browser to: **http://localhost:8000/api/recordings/**

## Features Available

- **Activity Timeline** - View all recorded species calls
- **Log a Call** - Submit new audio recordings
- **Analytics** - View species statistics and rankings
- **Recording Details** - Click any species name to see full details

## Adding New Recordings

To add recordings through the web interface:
1. Click "Log a Call" button (top right of Activity Timeline)
2. Fill in the form:
   - **Species:** Choose from dropdown (MUST add Species first in admin)
   - **Location:** Choose from dropdown (MUST add Location first in admin)
   - **Audio file:** Upload an MP3 or WAV file
   - **Date & Time:** Set when the recording was made
   - **Confidence Score:** Enter 0.0 to 1.0
3. Click "Submit Recording"
4. You'll be redirected to the recording detail page

## Admin Panel

Access the Django admin panel at **http://localhost:8000/admin/**

Here you can:
- Add/edit Species
- Add/edit Locations
- View all recordings
- Flag anomalies
- Manage user accounts

## Stopping the Server

Press **Ctrl + C** in the terminal to stop the server.

## Deactivating Virtual Environment

When you're done working:
```bash
deactivate
```

## Production Deployment

Before deploying to production:
1. Change `DEBUG = False` in `settings.py`
2. Update `ALLOWED_HOSTS` with your actual domain
3. Use environment variables for `SECRET_KEY`
4. Set up a proper database (PostgreSQL recommended)
5. Configure static and media file serving
6. Use a production WSGI server (gunicorn, uwsgi, etc.)

## Troubleshooting

**"No such table" error when starting server:**
- Run: `python manage.py migrate`

**"Species matching query does not exist" error on form:**
- YOU MUST ADD SPECIES via admin panel first (http://localhost:8000/admin/)

**"Location matching query does not exist" error on form:**
- YOU MUST ADD LOCATIONS via admin panel first (http://localhost:8000/admin/)

**"Permission denied" when uploading audio:**
- Check that the `media/` directory exists in the Assessment 2 folder

**"port 8000 is already in use":**
```bash
python manage.py runserver 8001
# Then go to http://localhost:8001/api/recordings/
```

**Virtual environment not activating:**
- Check you're in the Assessment 2 directory
- On Windows, you might need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first

## Project Structure

```
Assessment 2/
├── blog_app/                    # Main Django app
│   ├── models.py               # Database models
│   ├── views.py                # Page views
│   ├── forms.py                # Form for creating recordings
│   ├── urls.py                 # URL routing
│   ├── templates/              # App templates
│   │   ├── recording_list.html
│   │   ├── recording_detail.html
│   │   ├── recording_form.html
│   │   └── analytics.html
│   ├── static/
│   │   └── blog_app/
│   │       └── styles.css      # Custom styling
│   └── migrations/
├── project_blog/               # Django project settings
│   ├── settings.py             # Configuration
│   ├── urls.py                 # Main URL routing
│   └── wsgi.py
├── templates/
│   └── base.html               # Base template
├── media/                       # User uploads (created after clone)
├── manage.py                    # Django management
├── requirements.txt            # Python dependencies
├── db.sqlite3                  # Database (created after migrate)
└── venv/                       # Virtual environment (created locally)
```

## Need Help?

- Check that you're in the `Assessment 2` directory
- Make sure Python 3.10+ is installed: `python --version`
- Make sure virtual environment is activated (look for `(venv)` in terminal)
- Make sure you've run migrations: `python manage.py migrate`
- Make sure you've added Species and Locations in admin panel

