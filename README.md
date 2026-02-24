# Placement Tracker

A secure job application tracking system for students with authentication and Kanban-style dashboard built with Django.

## Features

- **Authentication**: User registration, login, and logout with session-based authentication
- **Job Application Tracking**: Create, read, update, and delete job applications
- **Kanban Dashboard**: Visual representation of applications across 6 status categories
- **Statistics**: Track total applications, interviews, offers, and success rate
- **Security**: Users can only access their own data with proper authorization
- **Status Management**: Business logic to prevent invalid status transitions
- **Responsive Design**: Clean UI built with Tailwind CSS

## Tech Stack

- Django 6.0+
- SQLite (default) / PostgreSQL (production)
- Django Templates
- Tailwind CSS (via CDN)
- Session-based authentication
- Gunicorn-compatible

## Setup Instructions

### Prerequisites

- Python 3.8+
- uv (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tracky
   ```

2. **Create and activate virtual environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open http://localhost:8000 in your browser
   - Register a new account or login with existing credentials

## Application Statuses

The system tracks applications through these stages:

1. **WISHLIST** - Companies you want to apply to
2. **APPLIED** - Applications submitted
3. **OA** - Online Assessment/Coding Test
4. **INTERVIEW** - Interview scheduled/completed
5. **OFFER** - Job offer received
6. **REJECTED** - Application rejected

**Business Rules:**
- Cannot move directly from WISHLIST to OFFER
- Status changes are logged to console
- Applications are sorted by most recent first

## Production Deployment

### Using Gunicorn

1. **Install production dependencies**
   ```bash
   uv pip install gunicorn
   ```

2. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn placement_tracker_project.wsgi:application --bind 0.0.0.0:8000
   ```

### Environment Variables

For production, set these environment variables:

```bash
export DJANGO_SETTINGS_MODULE=placement_tracker_project.settings
export SECRET_KEY='your-secret-key-here'
export DEBUG=False
export ALLOWED_HOSTS='your-domain.com,localhost'
```

### PostgreSQL Setup (Optional)

1. **Install PostgreSQL adapter**
   ```bash
   uv pip install psycopg2-binary
   ```

2. **Update settings.py database configuration**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'placement_tracker',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

## Project Structure

```
placement_tracker_project/
├── manage.py
├── placement_tracker_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tracker_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
│       ├── base.html
│       ├── registration/
│       │   ├── login.html
│       │   └── register.html
│       └── tracker/
│           ├── dashboard.html
│           ├── application_form.html
│           └── application_confirm_delete.html
├── static/
├── requirements.txt
└── README.md
```

## API Endpoints

- `/` - Dashboard (login required)
- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/create/` - Create new application (login required)
- `/edit/<uuid>/` - Update application (login required)
- `/delete/<uuid>/` - Delete application (login required)
- `/admin/` - Django admin interface

## Security Features

- CSRF protection enabled
- User data isolation (users can only access their own applications)
- Login required for all application-related views
- 404 errors for unauthorized access attempts
- Form validation on both client and server side

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.