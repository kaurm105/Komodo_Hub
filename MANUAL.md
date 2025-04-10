# Komodo Hub - Conservation Platform Setup Guide

## Project Overview
Komodo Hub is a Flask-based conservation platform focused on wildlife tracking, species reporting, and collaborative ecological research. The platform supports multiple user roles and provides features for education, tracking, and community engagement in wildlife conservation.

## Local Development Setup

### Prerequisites
1. Python 3.11 or higher
2. Git
3. pip (Python package installer)

Note: The application uses SQLite by default for easy local setup. PostgreSQL configuration is optional and only needed for production deployments.

### Step-by-Step Installation

1. System Dependencies:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql postgresql-contrib

# macOS (using Homebrew)
brew install python@3.11 postgresql

# Windows
# Download Python 3.11 from python.org
# Download PostgreSQL from postgresql.org
```

2. Clone the repository:
```bash
git clone <repository-url>
cd komodo-hub
```

3. Set up a virtual environment:
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

4. Install Python dependencies:
```bash
pip install flask==3.0.0
pip install flask-login==0.6.3
pip install flask-sqlalchemy==3.1.1
pip install flask-wtf==1.2.1
pip install gunicorn==21.2.0
pip install psycopg2-binary==2.9.9
pip install sqlalchemy==2.0.23
pip install email-validator==2.1.0.post1
pip install werkzeug==3.0.1
pip install wtforms==3.1.1
```

5. Database Setup:

SQLite (Default):
```
# No setup required! The application will automatically create a SQLite database
# file named 'komodo.db' in the project root directory.
```

PostgreSQL (Optional for Production):

a. Start PostgreSQL service:
```bash
# Linux
sudo service postgresql start

# macOS
brew services start postgresql

# Windows
# Use Task Manager or Services app
```

b. Create database and user:
```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE komodo_hub;
CREATE USER komodo_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE komodo_hub TO komodo_user;
\q
```

6. Environment Configuration:

Create a `.env` file in the project root:
```
# Database Configuration (SQLite - Default)
# Leave this commented out to use the default SQLite database
# DATABASE_URL=sqlite:///komodo.db

# Database Configuration (PostgreSQL - Optional for Production)
# DATABASE_URL=postgresql://komodo_user:your_password@localhost:5432/komodo_hub

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SESSION_SECRET=your-secret-key-here

# Optional: Email Configuration (if needed)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

7. Database Initialization:
```bash
# The application will automatically create and initialize the database on first run,
# including creating the database tables and populating them with sample data.
# It will also create test accounts with various user roles (see Test Accounts section).

# You do not need to manually create tables or users for development purposes.
```

### Running the Application

1. Start the Development Server:
```bash
# Make sure virtual environment is activated
flask run --host=0.0.0.0 --port=5000
```

2. Access the Application:
- Local: http://localhost:5000
- Network: http://<your-ip>:5000

### Troubleshooting Guide

1. Database Connection Issues:

For SQLite (Default):
```bash
# Check if SQLite database file exists
ls -la komodo.db

# Verify SQLite database
sqlite3 komodo.db .tables

# Common fixes:
# - Check if database file exists and has proper permissions
# - Verify no other process is locking the database
# - Backup and recreate database file if corrupted
```

For PostgreSQL (Production):
```bash
# Check PostgreSQL status
sudo service postgresql status

# Verify connection
psql -U komodo_user -d komodo_hub -h localhost

# Common fixes:
# - Check if PostgreSQL is running
# - Verify DATABASE_URL format
# - Ensure database exists
# - Check user permissions
```

2. Port Already in Use:
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>
```

3. Missing Dependencies:
```bash
# Verify Python version
python --version

# Check installed packages
pip list

# Reinstall dependencies
pip install -r requirements.txt
```

4. Permission Issues:
```bash
# Fix file permissions
chmod -R 755 .

# Fix database permissions
sudo -u postgres psql -c "ALTER USER komodo_user CREATEDB;"
```

### Testing

1. Test Accounts:
```
Teacher Account:
- Email: teacher@test.com
- Password: password123
- Role: Teacher

Community Account:
- Email: community@example.com
- Password: password123
- Role: Community Member

Student Account:
- Email: student1@example.com
- Password: password123
- Role: Student

Administrator Account:
- Email: admin@komodo.com
- Password: admin123
- Role: Admin (Full database control)
```

2. Feature Testing:
- Login/Logout
- Species Database Access
- Educational Resources
- Conservation Challenges
- User Management
- Forum Access

### Development Guidelines

1. Code Style:
- Follow PEP 8
- Use type hints
- Document functions
- Use consistent naming conventions

2. Git Workflow:
- Create feature branches
- Write descriptive commits
- Test before merging
- Follow conventional commits

3. Database Changes:
- Use SQLAlchemy migrations
- Never modify production data directly
- Back up before schema changes
- Test migrations locally first

4. Testing:
- Write unit tests for new features
- Perform integration testing
- Test all user roles
- Verify database operations

### Support and Maintenance

1. Logging:
- Check app.logger for application logs
- Review PostgreSQL logs
- Monitor error tracking
- Check system logs

2. Backup:
- Regular database backups
- Code repository backups
- Environment configuration backups
- User data exports

3. Updates:
- Weekly security updates
- Monthly feature releases
- Quarterly dependency updates
- Annual major version upgrades

4. Monitoring:
- Application health checks
- Database performance
- User activity monitoring
- Error rate tracking

### Security Best Practices

1. Authentication:
- Use strong password policies
- Implement rate limiting
- Enable session management
- Use secure cookie settings

2. Database:
- Use parameterized queries
- Encrypt sensitive data
- Regular security audits
- Backup encryption

3. Application:
- CSRF protection
- XSS prevention
- Input validation
- Output sanitization

---
Last Updated: April 01, 2025
Note: This manual is regularly updated as new features are implemented or existing features are modified.