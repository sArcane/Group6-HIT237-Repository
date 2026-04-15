# Setup Guide for Local Development

## Prerequisites
- Python 3.10 or higher
- pip package manager

## Installation Steps

### 1. Clone and Navigate to Project
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/Group6-HIT237-Repository.git

# Navigate to the project folder
cd Group6-HIT237-Repository

# Go to Assessment 2 directory
cd "Assessment 2"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate      # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Media Directory (for audio uploads)
```bash
mkdir media
```

### 5. Setup Database
```bash
python manage.py migrate
```

### 6. Create Admin User (optional but recommended)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### 7. Add Test Data (Species & Locations)
Via Django Admin Panel:
1. Start the server: `python manage.py runserver`
2. Go to http://localhost:8000/admin/
3. Log in with your admin credentials
4. Add a few Species (e.g., "Kookaburra", "Black Cockatoo")
5. Add a few Locations (e.g., "Melbourne", "Sydney")

### 8. Start the Development Server
```bash
python manage.py runserver
```

Open your browser to `http://localhost:8000/api/recordings/`

## Features Available

- **Activity Timeline** - View all recorded species calls
- **Log a Call** - Submit new audio recordings
- **Analytics** - View species statistics and rankings
- **Recording Details** - Click any species name to see full details

## Adding New Recordings

To add recordings through the web interface:
1. Click "Log a Call" button or navigate to `/api/recordings/new/`
2. Fill in the form:
   - Select a Species
   - Select a Location
   - Upload an audio file
   - Set the recording date/time
   - Enter your confidence score (0.0-1.0)
3. Click "Submit Recording"

## Admin Panel

Access the Django admin panel at `/admin/` to:
- Add/edit Species and Locations
- View all recordings
- Flag anomalies
- Manage users

## Production Deployment

Before deploying to production:
1. Change `DEBUG = False` in `settings.py`
2. Update `ALLOWED_HOSTS` with your actual domain
3. Use environment variables for `SECRET_KEY`
4. Set up a proper database (PostgreSQL recommended)
5. Configure static and media file serving
6. Use a production WSGI server (gunicorn, uwsgi, etc.)

## Troubleshooting

**"Species matching query does not exist" error on form:**
- You need to add Species entries via the admin panel first

**"Location matching query does not exist" error on form:**
- You need to add Location entries via the admin panel first

**"Permission denied" when uploading audio:**
- Check that the `media/` directory exists and is writable

**Database locked error:**
- Delete `db.sqlite3` and run migrations again: `python manage.py migrate`

## Support

The project structure:
- `blog_app/` - Main Django app with views, models, forms
- `project_blog/` - Django project settings
- `templates/` - HTML templates (base layout)
- `blog_app/templates/` - App-specific templates
- `blog_app/static/` - CSS and other static files
