from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_data():
    # Import models here to avoid circular imports
    from app import db
    from models import Species, EducationalResource, ConservationProgram, User

    # Create default accounts if they don't exist
    test_accounts = [
        {
            "username": "testteacher",
            "email": "teacher@test.com",
            "password": "password123",
            "role": "teacher"
        },
        {
            "username": "teststudent",
            "email": "student@test.com",
            "password": "password123",
            "role": "student"
        }
    ]

    for account in test_accounts:
        if not User.query.filter_by(email=account["email"]).first():
            user = User(
                username=account["username"],
                email=account["email"],
                role=account["role"],
                password_hash=generate_password_hash(account["password"])
            )
            db.session.add(user)

    db.session.commit()

    # Get teacher account for creating resources
    teacher = User.query.filter_by(email="teacher@test.com").first()

    # Add sample species if none exist
    if Species.query.count() == 0:
        species_data = [
            {
                "name": "Komodo Dragon",
                "scientific_name": "Varanus komodoensis",
                "description": "The Komodo dragon is the largest living lizard species.",
                "population": 3000,
                "conservation_status": "Endangered",
                "habitat": "Indonesian islands",
                "threats": "Habitat loss, human conflict"
            },
            {
                "name": "Sumatran Tiger",
                "scientific_name": "Panthera tigris sumatrae",
                "description": "The smallest of all tiger subspecies.",
                "population": 400,
                "conservation_status": "Critically Endangered",
                "habitat": "Tropical forests",
                "threats": "Poaching, deforestation"
            }
        ]

        for species in species_data:
            db.session.add(Species(**species))

    # Add educational resources if none exist
    if EducationalResource.query.count() == 0:
        resources = [
            {
                "title": "Introduction to Wildlife Conservation",
                "content": "Learn about the basics of wildlife conservation and biodiversity.",
                "author_id": teacher.id,
                "resource_type": "article"
            },
            {
                "title": "Field Research Techniques",
                "content": "Essential methods for wildlife research and monitoring.",
                "author_id": teacher.id,
                "resource_type": "guide"
            }
        ]

        for resource in resources:
            db.session.add(EducationalResource(**resource))

    # Add conservation programs if none exist
    if ConservationProgram.query.count() == 0:
        programs = [
            {
                "title": "Save the Komodo",
                "description": "Protection program for Komodo dragons.",
                "location": "Komodo Island",
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=365),
                "coordinator_id": teacher.id
            }
        ]

        for program in programs:
            db.session.add(ConservationProgram(**program))

    db.session.commit()

if __name__ == "__main__":
    from app import app
    with app.app_context():
        init_data()