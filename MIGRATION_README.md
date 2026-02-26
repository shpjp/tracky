# Placement Tracker - JWT Authentication & Neon DB Migration

This document outlines the migration from SQLite to Neon DB with JWT authentication implementation.

## 🚀 New Features Implemented

### 1. JWT Authentication System
- **Access Tokens**: Short-lived tokens (60 minutes) for API authentication
- **Refresh Tokens**: Long-lived tokens (7 days) for token renewal
- **Token Rotation**: Automatic refresh token rotation for enhanced security
- **Token Blacklisting**: Ability to revoke tokens on logout/password change

### 2. Enhanced Security
- **Bcrypt Password Hashing**: Industry-standard password hashing
- **Email-based Authentication**: Users can login with email or username
- **Password Validation**: Comprehensive password requirements
- **Token Management**: Track and manage user sessions

### 3. Database Migration
- **Neon DB Integration**: PostgreSQL-based cloud database
- **Custom User Model**: Extended user model with additional fields
- **Data Migration Tools**: Automated user data migration utilities

## 🛠 Setup Instructions

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
SECRET_KEY=your-super-secret-django-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://username:password@your-neon-endpoint/dbname?sslmode=require
```

### 2. Neon DB Setup

1. **Create Neon Account**: Visit [neon.tech](https://neon.tech) and create an account
2. **Create Database**: Create a new PostgreSQL database
3. **Get Connection String**: Copy the connection string from Neon dashboard
4. **Update DATABASE_URL**: Paste the connection string in your `.env` file

Example Neon connection string:
```
postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/dbname?sslmode=require
```

### 3. Dependencies Installation

The following packages have been added:
- `djangorestframework>=3.14.0` - API framework
- `djangorestframework-simplejwt>=5.3.0` - JWT authentication
- `django-cors-headers>=4.3.1` - CORS support
- `bcrypt>=4.1.2` - Password hashing
- `PyJWT>=2.8.0` - JWT token handling

### 4. Database Migration

Run the following commands:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Migrate existing users (if any)
python manage.py migrate_users --dry-run  # Preview migration
python manage.py migrate_users            # Actual migration

# Create superuser
python manage.py createsuperuser
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (get tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout (revoke tokens)

### User Management
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update user profile
- `POST /api/user/change-password/` - Change password
- `GET /api/user/tokens/` - List active tokens
- `POST /api/user/tokens/{id}/revoke/` - Revoke specific token

### Applications
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Create application
- `GET /api/applications/{id}/` - Get application details
- `PUT /api/applications/{id}/` - Update application
- `DELETE /api/applications/{id}/` - Delete application

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics

## 🔐 Authentication Flow

### Registration/Login
```json
// Registration
POST /api/auth/register/
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
}

// Response
{
    "message": "User registered successfully",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "email": "john@example.com",
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

### Token Usage
```javascript
// Include in request headers
Authorization: Bearer <access_token>

// Example API call
fetch('/api/applications/', {
    headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
    }
})
```

### Token Refresh
```json
POST /api/auth/refresh/
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

// Response
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  // New refresh token if rotation enabled
}
```

## 🔧 Configuration Details

### JWT Settings
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Password Hashing
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  # Primary
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',       # Fallback
    # ... other hashers
]
```

### Database Configuration
```python
# Optimized for Neon DB
DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL, 
        conn_max_age=600, 
        conn_health_checks=True
    )
}
```

## 🧪 Testing the Implementation

### 1. Test Registration
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'
```

### 2. Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 3. Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🚨 Important Notes

1. **Backup Data**: Always backup your existing database before migration
2. **Environment Variables**: Never commit `.env` files to version control
3. **Secret Key**: Generate a new secret key for production
4. **SSL/TLS**: Ensure HTTPS is enabled in production
5. **Token Security**: Store tokens securely in the frontend (httpOnly cookies recommended)

## 🔄 Migration Checklist

- [ ] ✅ Updated requirements.txt with new dependencies
- [ ] ✅ Created CustomUser model with bcrypt hashing
- [ ] ✅ Implemented JWT authentication system
- [ ] ✅ Added refresh token management
- [ ] ✅ Created comprehensive API endpoints
- [ ] ✅ Updated settings for Neon DB configuration
- [ ] ✅ Added CORS support for frontend integration
- [ ] ✅ Created user migration management command
- [ ] ✅ Implemented email-based authentication backend
- [ ] 🔄 Configure Neon DB connection (user action required)
- [ ] 🔄 Run migrations on production database
- [ ] 🔄 Update frontend to use new API endpoints
- [ ] 🔄 Test all authentication flows

## 🆘 Troubleshooting

### Common Issues

1. **Migration Errors**
   - Ensure DATABASE_URL is correctly set
   - Check Neon DB connection is active
   - Run migrations with `--verbosity=2` for detailed output

2. **JWT Token Issues**
   - Verify SECRET_KEY is set and consistent
   - Check token expiration times
   - Ensure proper Authorization header format

3. **Authentication Problems**
   - Verify email/username spelling
   - Check password hashing compatibility
   - Review authentication backend configuration

4. **CORS Errors**
   - Update CORS_ALLOWED_ORIGINS in settings
   - Check frontend domain is included
   - Verify credentials are allowed

## 📚 Additional Resources

- [Neon DB Documentation](https://neon.tech/docs)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Bcrypt Documentation](https://pypi.org/project/bcrypt/)

---

**Security Notice**: This implementation follows industry best practices for JWT authentication and password security. Always review and test thoroughly before deploying to production.