# 🎯 Tracky - Placement Tracker Application

A modern Django-based web application for tracking job applications and placements with JWT authentication, bcrypt security, and Neon PostgreSQL database.

## ✨ Features

- **🔐 JWT Authentication** - Secure access/refresh token system
- **🛡️ Bcrypt Password Hashing** - Industry-standard password security  
- **🗄️ Neon PostgreSQL** - Cloud-native database with auto-scaling
- **📊 Application Tracking** - Comprehensive job application management
- **📈 Dashboard Analytics** - Visual insights into your placement journey
- **🎨 Modern UI** - Tailwind CSS for responsive design
- **🔄 Token Rotation** - Enhanced security with refresh token rotation
- **📧 Email Authentication** - Login with email or username
- **🚪 Secure Logout** - Token blacklisting for enhanced security

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for Tailwind CSS)
- [uv](https://docs.astral.sh/uv/) package manager
- Neon Database account

### 1. Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd tracky

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
uv pip install -r requirements.txt

# Install Node.js dependencies for Tailwind
npm install
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configurations
nano .env  # or use your preferred editor
```

**Required .env variables:**
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://username:password@endpoint/database?sslmode=require
```

### 3. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create test data (optional)
python manage.py shell < test_auth.py
```

### 4. Build CSS & Start Server

```bash
# Build Tailwind CSS
npm run build-css

# Start development server
python manage.py runserver 8080
```

Visit: `http://127.0.0.1:8080`

## 🛠️ Technology Stack

### Backend
- **Django 5.0+** - Web framework
- **Django REST Framework** - API development
- **SimpleJWT** - JWT authentication
- **Neon PostgreSQL** - Cloud database
- **Bcrypt** - Password hashing

### Frontend
- **HTML5 & CSS3** - Structure and styling
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript (ES6+)** - Interactive functionality
- **PostCSS** - CSS processing

### Development Tools
- **uv** - Fast Python package manager
- **npm** - Node.js package manager
- **Git** - Version control

## 📁 Project Structure

```
tracky/
├── 📄 manage.py                      # Django management script
├── 📁 placement_tracker_project/     # Main project settings
│   ├── settings.py                   # Django configuration
│   ├── urls.py                       # Root URL configuration
│   └── wsgi.py                       # WSGI configuration
├── 📁 tracker_app/                   # Main application
│   ├── 📄 models.py                  # Database models (CustomUser, Application)
│   ├── 📄 views.py                   # Django views (login/logout)
│   ├── 📄 api_views.py               # REST API endpoints
│   ├── 📄 serializers.py             # DRF serializers
│   ├── 📄 backends.py                # Custom authentication backend
│   ├── 📄 forms.py                   # Django forms
│   ├── 📄 admin.py                   # Admin interface
│   ├── 📁 templates/                 # HTML templates
│   ├── 📁 migrations/                # Database migrations
│   └── 📁 management/commands/       # Custom management commands
├── 📁 static/                        # Static files (CSS, JS, images)
├── 📄 requirements.txt               # Python dependencies
├── 📄 package.json                   # Node.js dependencies
├── 📄 tailwind.config.js             # Tailwind configuration
├── 📄 postcss.config.js              # PostCSS configuration
├── 📄 .env.example                   # Environment template
└── 📄 README.md                      # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (returns JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout (blacklist tokens)

### User Management
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update user profile
- `POST /api/user/change-password/` - Change password

### Applications
- `GET /api/applications/` - List user's applications
- `POST /api/applications/` - Create new application
- `GET /api/applications/{id}/` - Get specific application
- `PUT /api/applications/{id}/` - Update application
- `DELETE /api/applications/{id}/` - Delete application

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics

## 🧪 Testing

### Manual Testing Scripts

```bash
# Test authentication endpoints
python test_auth.py

# Test API endpoints
python test_api.py
```

### API Testing with cURL

```bash
# Register new user
curl -X POST http://127.0.0.1:8080/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password_confirm":"testpass123"}'

# Login
curl -X POST http://127.0.0.1:8080/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# Access protected endpoint (replace TOKEN with actual access token)
curl -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:8080/api/user/profile/
```

## 🛡️ Security Features

- **🔐 JWT Authentication** - Stateless, secure token-based auth
- **🔄 Token Rotation** - Automatic refresh token rotation
- **🛡️ Bcrypt Hashing** - Strong password hashing (cost factor: 12)
- **🚫 Token Blacklisting** - Secure logout with token revocation
- **📧 Email Validation** - Proper email format validation
- **🔒 CORS Protection** - Configured for secure frontend integration
- **🛡️ SQL Injection Protection** - Django ORM prevents SQL injection
- **🔐 CSRF Protection** - Built-in Django CSRF protection

## 🚀 Deployment

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key-very-long-and-random
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong, unique `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up Neon database with proper connection pooling
- [ ] Configure static file serving
- [ ] Set up SSL/TLS certificates
- [ ] Configure email backend for notifications
- [ ] Set up monitoring and logging

## 🗄️ Database Schema

### CustomUser Model
```python
- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Bcrypt hashed)
- first_name, last_name
- is_active, is_staff, is_superuser
- date_joined, last_login
```

### Application Model
```python
- id (Primary Key)
- user (Foreign Key to CustomUser)
- company_name
- role
- status (Applied, Interview, Offer, Rejected)
- applied_date
- notes
- created_at, updated_at
```

### RefreshToken Model
```python
- id (Primary Key)
- user (Foreign Key to CustomUser)
- token (Unique)
- created_at
- is_blacklisted
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check your DATABASE_URL in .env
# Ensure Neon database is running
# Verify SSL settings
```

**2. Migration Issues**
```bash
# Reset migrations if needed
rm tracker_app/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

**3. CSS Not Loading**
```bash
# Rebuild Tailwind CSS
npm run build-css
python manage.py collectstatic
```

**4. JWT Token Issues**
```bash
# Check token expiration
# Verify JWT_SECRET_KEY matches
# Ensure proper Authorization header format
```

### Getting Help

- 📖 Check the [MIGRATION_README.md](MIGRATION_README.md) for detailed setup
- 🐛 Open an issue for bugs
- 💬 Start a discussion for questions
- 📧 Contact: [your-email@example.com]

## 🎯 Roadmap

- [ ] 📧 Email verification system
- [ ] 📱 Mobile app with React Native
- [ ] 📊 Advanced analytics dashboard
- [ ] 🔔 Push notifications
- [ ] 📄 Resume builder integration
- [ ] 🤖 AI-powered job recommendations
- [ ] 📈 Application tracking automation
- [ ] 🔗 LinkedIn integration

---

**Made with ❤️ by [Your Name]**

*Helping students track their placement journey, one application at a time.*