# Local Setup Guide for Komodo Hub

This guide provides step-by-step instructions for setting up and running the Komodo Hub application on your local machine using SQLite.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Clone the Repository

Clone the repository to your local machine or download and extract the ZIP file.

### 2. Create and Activate a Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or with pip3:

```bash
pip3 install -r requirements.txt
```

### 4. Environment Variables Setup

Create a `.env` file in the root directory with the following content:

```
# SQLite configuration
SQLITE_PATH=instance/komodo.db
SESSION_SECRET=your_secret_key_here

# Logging level
LOG_LEVEL=DEBUG
```

Replace `your_secret_key_here` with a secure random string for production use.

### 5. Database Initialization

The application is configured to automatically create the SQLite database file and necessary tables when started. The database file will be created in the `instance/` directory.

### 6. Run the Application

```bash
# Run with the Flask development server
python main.py
```

The application will be available at: http://localhost:5000

## Troubleshooting

### Common Issues and Solutions

1. **"No module named 'flask'"**
   - Make sure you've activated your virtual environment and installed all requirements.
   
2. **"Error: Unable to open database file"**
   - Check that the `instance` directory exists in your project root. Create it if missing:
     ```bash
     mkdir -p instance
     ```
   - Verify that the application has write permissions to the directory.

3. **"Table already exists" or other database migration issues**
   - Remove the existing database file and let the application create a new one:
     ```bash
     rm instance/komodo.db
     ```

4. **Server doesn't start or crashes immediately**
   - Check the log file (`app.log`) for detailed error messages.
   - Verify that no other application is using port 5000.

## Application Structure

The Komodo Hub application is structured as follows:

```
komodo_hub/
├── app.py                  # Main application configuration
├── main.py                 # Application entry point
├── models.py               # Database models
├── forms.py                # Form definitions
├── routes.py               # Main routes (if not using blueprints)
├── .env                    # Environment variables
├── instance/               # Instance-specific data (including SQLite database)
│   └── komodo.db           # SQLite database file (created automatically)
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
├── templates/              # HTML templates
├── blueprints/             # Feature-specific modules
│   ├── auth.py             # Authentication routes
│   ├── forum.py            # Forum functionality
│   └── ...
└── scripts/                # Utility scripts
    └── init_data.py        # Database initialization script
```

## User Accounts

After initial setup, the application creates a test teacher account:
- Email: teacher@test.com
- Password: password123

You can use this account to log in or create your own accounts through the registration page.

## Additional Information

- The application uses SQLite for local development, which does not require any additional database server setup.
- All uploaded files and user data are stored locally in the `instance` directory.
- For production deployment, consider using a more robust database solution like PostgreSQL.