# Komodo Hub - Digital Platform for Community-Supported Animal Conservation

## Overview
Komodo Hub is a Flask-based web application designed to support animal conservation efforts through community engagement. The platform provides role-based access for teachers, students, and community members to participate in wildlife conservation activities.

## Features

### Core Functionality
- Multi-role authentication system
- Species database and sighting reports
- Educational resource management
- Interactive community forum
- Progress tracking and analytics

### Role-Specific Features

#### Teacher Dashboard
- Content management
- Student progress tracking
- Sighting verification
- Analytics dashboard

#### Student Interface
- Interactive learning materials
- Species identification
- Progress tracking
- Sighting reports

#### Community Member Access
- Conservation program participation
- Species sighting reports
- Resource library access
- Forum engagement

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Required Python packages (see pyproject.toml)

### Installation
1. Clone the repository
2. Create a Python virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
# Using requirements.txt
pip install -r requirements.txt

# Or using pyproject.toml
pip install .
```

4. Set up environment variables (create a .env file or export directly):
```bash
# Required settings
DATABASE_URL=postgresql://username:password@localhost:5432/komodo_hub
SESSION_SECRET=your_secure_random_secret_key

# Optional: Default SQLite fallback if DATABASE_URL is not provided
# The app will automatically use SQLite if PostgreSQL connection is not available
```

5. Initialize the database (if new installation):
```bash
# The application will automatically create tables on first run
# To populate with sample data, run:
python scripts/init_data.py
```

### Running the Application
```bash
# Development mode
python main.py

# Production mode with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

The application will be available at `http://localhost:5000`

### Troubleshooting Common Issues

#### Database Connection Issues
- Ensure PostgreSQL is running and accessible
- Check that DATABASE_URL environment variable is correctly formatted
- The application provides a SQLite fallback for local development

#### Library/Resource Access Errors
- If you encounter "Resource not found" errors, ensure all blueprints are registered in app.py
- If dashboard shows an error, verify URL endpoints in the dashboard templates

#### Role-Based Access Problems
- Default roles are 'teacher', 'student', and 'community'
- Each role has specific dashboard templates and permissions

## Technical Stack

### Backend
- Flask web framework
- PostgreSQL database
- SQLAlchemy ORM
- Flask-Login authentication

### Frontend
- Bootstrap 5
- Custom CSS/JS
- Chart.js
- Leaflet.js maps

## Documentation
For detailed documentation, including:
- Complete feature list
- API endpoints
- Database schema
- Development guidelines

Please refer to [MANUAL.md](MANUAL.md)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
This project is proprietary and confidential.

## Support
For support and inquiries, please contact the development team.