import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Configure logging using environment variable
log_level = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

# Create Flask app
app = Flask(__name__)

# Set secret key with fallback
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database with SQLite as default and PostgreSQL as optional
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    # Handle Heroku-style PostgreSQL URLs if explicitly provided
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.logger.info("Using PostgreSQL database")
else:
    # Use SQLite with default Flask instance path
    database_url = "sqlite:///komodo.db"
    app.logger.info(f"Using SQLite database at: {database_url}")
    
    # Check if database directory is writable
    try:
        with open("komodo.db", 'a'):
            pass
        app.logger.info("SQLite database path is writable")
    except IOError as e:
        app.logger.error(f"SQLite database path is not writable: {str(e)}")
        # Fall back to memory database if file cannot be written
        database_url = "sqlite:///:memory:"
        app.logger.warning("Falling back to in-memory SQLite database")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Make the app publicly accessible
app.config['SERVER_NAME'] = None
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Initialize extensions with app
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Add Jinja filters and global functions
@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Format a datetime object to string."""
    if value is None:
        return ""
    return value.strftime(format)

# Add current datetime function for templates
@app.context_processor
def utility_processor():
    return {'now': datetime.now}

# Import models and register user loader
from models import User, Species, EducationalResource, ConservationProgram, LibraryResource
from models import ForumCategory, ForumThread, ForumPost

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def create_sample_data():
    """Create sample data if the database is empty"""
    try:
        # Check if we have any existing data
        if User.query.first() is None:
            app.logger.info("Creating sample data...")

            # Create a test teacher account
            teacher = User(
                username="test_teacher",
                email="teacher@test.com",
                role="teacher"
            )
            teacher.set_password("password123")
            db.session.add(teacher)
            
            # Create a test community account
            community = User(
                username="nature_lover",
                email="community@example.com",
                role="community"
            )
            community.set_password("password123")
            db.session.add(community)
            
            # Create a test student account
            student = User(
                username="student1",
                email="student1@example.com",
                role="student"
            )
            student.set_password("password123")
            db.session.add(student)
            
            # Create an admin account with full database control
            admin = User(
                username="admin",
                email="admin@komodo.com",
                role="admin",
                is_admin=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            app.logger.info("Created admin account")
            
            # Flush to get the user IDs
            db.session.flush()

            # Create enhanced species data
            species_data = [
                {
                    "name": "Komodo Dragon",
                    "scientific_name": "Varanus komodoensis",
                    "description": "The largest living species of lizard, found in Indonesian islands. Can grow up to 3 meters long and weigh over 70 kg.",
                    "conservation_status": "EN",
                    "habitat": "Tropical savanna forests",
                    "threats": "Habitat loss, human conflict, poaching",
                    "population": 3000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Sumatran Tiger",
                    "scientific_name": "Panthera tigris sumatrae",
                    "description": "A rare tiger subspecies native to the Indonesian island of Sumatra, with distinctive dark stripes and a reddish-orange coat.",
                    "conservation_status": "CR",
                    "habitat": "Tropical forests",
                    "threats": "Poaching, deforestation, human-wildlife conflict",
                    "population": 400,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Javan Rhino",
                    "scientific_name": "Rhinoceros sondaicus",
                    "description": "One of the most endangered large mammals in the world, with only a small population remaining in Indonesia's Ujung Kulon National Park.",
                    "conservation_status": "CR",
                    "habitat": "Lowland tropical rainforests",
                    "threats": "Habitat loss, poaching, small population size",
                    "population": 72,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Sumatran Orangutan",
                    "scientific_name": "Pongo abelii",
                    "description": "A critically endangered species of great ape native to Indonesia's Sumatra island, known for their intelligence and distinctive reddish fur.",
                    "conservation_status": "CR",
                    "habitat": "Tropical rainforests",
                    "threats": "Deforestation, palm oil plantations, illegal pet trade",
                    "population": 14000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Bali Starling",
                    "scientific_name": "Leucopsar rothschildi",
                    "description": "A beautiful white bird endemic to Bali, Indonesia, with blue skin around the eyes and a long, drooping crest.",
                    "conservation_status": "CR",
                    "habitat": "Dry, open forests",
                    "threats": "Illegal capture for pet trade, habitat loss",
                    "population": 100,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Sumatran Elephant",
                    "scientific_name": "Elephas maximus sumatranus",
                    "description": "A subspecies of the Asian elephant native to Sumatra, recognizable by their smaller size and relatively larger ears.",
                    "conservation_status": "CR",
                    "habitat": "Lowland forests",
                    "threats": "Habitat loss, human-elephant conflict, poaching",
                    "population": 2400,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Banteng",
                    "scientific_name": "Bos javanicus",
                    "description": "A species of wild cattle found in Southeast Asia, with a distinctive white patch on the hindquarters.",
                    "conservation_status": "EN",
                    "habitat": "Dry, deciduous forests and grasslands",
                    "threats": "Hunting, habitat loss, hybridization with domestic cattle",
                    "population": 8000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Sumatran Rhinoceros",
                    "scientific_name": "Dicerorhinus sumatrensis",
                    "description": "The smallest of all rhino species and the only Asian rhino with two horns, covered with long hair.",
                    "conservation_status": "CR",
                    "habitat": "Dense mountain forests",
                    "threats": "Poaching, habitat loss, small population",
                    "population": 80,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Malayan Tapir",
                    "scientific_name": "Tapirus indicus",
                    "description": "The largest of the five tapir species, characterized by their distinctive black and white pattern resembling an oreo cookie.",
                    "conservation_status": "EN",
                    "habitat": "Tropical forests",
                    "threats": "Habitat destruction, hunting, road kills",
                    "population": 2500,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Clouded Leopard",
                    "scientific_name": "Neofelis nebulosa",
                    "description": "A wild cat with distinctive cloud-like patterns on its coat and exceptionally long canine teeth.",
                    "conservation_status": "VU",
                    "habitat": "Tropical forests",
                    "threats": "Deforestation, poaching for fur and bones",
                    "population": 10000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Proboscis Monkey",
                    "scientific_name": "Nasalis larvatus",
                    "description": "An endemic monkey species to Borneo, known for the male's large pendulous nose used to attract females.",
                    "conservation_status": "EN",
                    "habitat": "Mangrove, riverine, and swamp forests",
                    "threats": "Habitat loss, hunting",
                    "population": 7000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Sunda Pangolin",
                    "scientific_name": "Manis javanica",
                    "description": "A critically endangered mammal covered in protective scales, hunted for its meat and scales used in traditional medicine.",
                    "conservation_status": "CR",
                    "habitat": "Secondary, disturbed forests",
                    "threats": "Illegal wildlife trade, habitat loss",
                    "population": 1000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Babirusa",
                    "scientific_name": "Babyrousa babyrussa",
                    "description": "An unusual pig species with tusks that grow upward through the snout and curve backward toward the forehead.",
                    "conservation_status": "VU",
                    "habitat": "Tropical forests, riverbanks",
                    "threats": "Hunting, habitat loss",
                    "population": 4000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Anoa",
                    "scientific_name": "Bubalus depressicornis",
                    "description": "A small, forest-dwelling buffalo endemic to Sulawesi, with straight horns and a dark brown to black coat.",
                    "conservation_status": "EN",
                    "habitat": "Lowland and mountain forests",
                    "threats": "Hunting, habitat loss",
                    "population": 5000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Javan Hawk-eagle",
                    "scientific_name": "Nisaetus bartelsi",
                    "description": "A medium-large bird of prey endemic to Java, recognized as Indonesia's national bird.",
                    "conservation_status": "EN",
                    "habitat": "Tropical forests",
                    "threats": "Habitat loss, capture for pet trade",
                    "population": 600,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Dugong",
                    "scientific_name": "Dugong dugon",
                    "description": "A marine mammal related to manatees, feeding exclusively on seagrass in coastal waters around Indonesia.",
                    "conservation_status": "VU",
                    "habitat": "Shallow coastal waters with seagrass beds",
                    "threats": "Hunting, boat strikes, habitat degradation",
                    "population": 1000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Irrawaddy Dolphin",
                    "scientific_name": "Orcaella brevirostris",
                    "description": "A small dolphin with a rounded head and no beak, found in coastal areas and major river systems.",
                    "conservation_status": "EN",
                    "habitat": "Coastal, brackish and freshwater systems",
                    "threats": "Bycatch in fishing gear, habitat degradation",
                    "population": 7500,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Green Turtle",
                    "scientific_name": "Chelonia mydas",
                    "description": "A large sea turtle with a heart-shaped shell, named for the greenish color of its fat rather than its shell.",
                    "conservation_status": "EN",
                    "habitat": "Tropical and subtropical waters worldwide",
                    "threats": "Egg collection, hunting, plastic pollution, climate change",
                    "population": 85000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Leatherback Sea Turtle",
                    "scientific_name": "Dermochelys coriacea",
                    "description": "The largest of all living turtles, lacking a bony shell and instead covered with leathery skin.",
                    "conservation_status": "CR",
                    "habitat": "Open ocean, nests on tropical beaches",
                    "threats": "Egg collection, bycatch, plastic pollution",
                    "population": 26000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Sulawesi Bear Cuscus",
                    "scientific_name": "Ailurops ursinus",
                    "description": "A large marsupial with thick fur and a prehensile tail, endemic to Sulawesi.",
                    "conservation_status": "VU",
                    "habitat": "Tropical forests",
                    "threats": "Hunting, habitat loss",
                    "population": 9000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Black Crested Macaque",
                    "scientific_name": "Macaca nigra",
                    "description": "A monkey species endemic to Sulawesi, with an entirely jet-black body and distinctive crest of hair.",
                    "conservation_status": "CR",
                    "habitat": "Tropical rainforests",
                    "threats": "Hunting for bushmeat, habitat loss, pet trade",
                    "population": 5000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Sumatran Laughingthrush",
                    "scientific_name": "Garrulax bicolor",
                    "description": "A striking bird with pure white plumage and a black face mask, known for its beautiful song.",
                    "conservation_status": "EN",
                    "habitat": "Mountain forests",
                    "threats": "Capture for cage bird trade, habitat loss",
                    "population": 2500,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Wallace's Flying Frog",
                    "scientific_name": "Rhacophorus nigropalmatus",
                    "description": "A large tree frog with webbed feet that allow it to glide through the air when jumping from trees.",
                    "conservation_status": "LC",
                    "habitat": "Tropical rainforests",
                    "threats": "Habitat loss, climate change",
                    "population": 10000,
                    "created_by_id": teacher.id
                },
                {
                    "name": "Bornean Orangutan",
                    "scientific_name": "Pongo pygmaeus",
                    "description": "A critically endangered great ape native to Borneo, with distinctive red-orange hair and slower movements than its Sumatran cousin.",
                    "conservation_status": "CR",
                    "habitat": "Tropical and subtropical moist broadleaf forests",
                    "threats": "Deforestation, palm oil plantations, illegal hunting",
                    "population": 104700,
                    "created_by_id": teacher.id
                }
            ]

            for data in species_data:
                species = Species(**data)
                db.session.add(species)

            # Create enhanced library resources
            resources_data = [
                {
                    "title": "Conservation Basics",
                    "content": "An introduction to wildlife conservation principles and practices, covering the fundamental concepts of biodiversity preservation, habitat protection, and sustainable resource management.",
                    "resource_type": "article",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Field Research Guide",
                    "content": "Best practices for conducting wildlife field research, including observation techniques, data collection methods, and ethical considerations when working with animals in their natural habitats.",
                    "resource_type": "guide",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Komodo Dragon Biology",
                    "content": "A comprehensive overview of Komodo dragon biology, behavior, and ecology. Includes information on their unique hunting techniques, reproductive strategies, and evolutionary history.",
                    "resource_type": "research",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Indonesian Rainforest Ecosystems",
                    "content": "An exploration of the diverse rainforest ecosystems found across the Indonesian archipelago, highlighting their unique flora and fauna and the conservation challenges they face.",
                    "resource_type": "article",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Wildlife Photography Ethics",
                    "content": "Ethical guidelines for wildlife photography, ensuring that photographers minimize their impact on animal behavior and habitats while capturing compelling images.",
                    "resource_type": "guide",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Orangutan Conservation Status Report",
                    "content": "A detailed report on the current conservation status of orangutans in Sumatra and Borneo, including population trends, threats, and ongoing conservation initiatives.",
                    "resource_type": "research",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Bird Identification in Java",
                    "content": "A practical guide to identifying common and rare bird species found on the island of Java, with descriptions, habitat information, and behavioral cues.",
                    "resource_type": "guide",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Marine Conservation Challenges",
                    "content": "An overview of the unique challenges facing marine conservation efforts in Indonesia's coral reef ecosystems, including climate change impacts, fishing practices, and pollution.",
                    "resource_type": "article",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Traditional Ecological Knowledge",
                    "content": "The importance of incorporating traditional ecological knowledge from indigenous communities into modern conservation practices in Indonesia.",
                    "resource_type": "research",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Wildlife Tracking Techniques",
                    "content": "A guide to various wildlife tracking techniques, from traditional skills to modern GPS and satellite technologies used in conservation research.",
                    "resource_type": "guide",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Conservation Genetics Primer",
                    "content": "An introduction to the field of conservation genetics and its applications in preserving endangered species through understanding genetic diversity and population structure.",
                    "resource_type": "research",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Climate Change Impacts on Indonesian Biodiversity",
                    "content": "Research findings on how climate change is affecting Indonesia's unique biodiversity, with case studies from various ecosystems across the archipelago.",
                    "resource_type": "research",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Community-Based Conservation Success Stories",
                    "content": "Examples of successful community-based conservation initiatives from across Indonesia, highlighting how local involvement can lead to sustainable outcomes.",
                    "resource_type": "article",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Wildlife Rehabilitation Best Practices",
                    "content": "Guidelines for the rehabilitation and release of injured or orphaned wildlife, with specific considerations for Indonesian species.",
                    "resource_type": "guide",
                    "author_id": teacher.id,
                    "is_public": True
                },
                {
                    "title": "Ecotourism Development Guide",
                    "content": "A practical guide for developing ecotourism initiatives that benefit both local communities and wildlife conservation efforts in Indonesia.",
                    "resource_type": "guide",
                    "author_id": teacher.id,
                    "is_public": True
                }
            ]

            for data in resources_data:
                resource = LibraryResource(**data)
                db.session.add(resource)

            # Create forum categories
            forum_categories = [
                {
                    "name": "Conservation News",
                    "description": "Latest news and updates about conservation efforts in Indonesia and around the world."
                },
                {
                    "name": "Species Discussion",
                    "description": "Discuss various endangered species, their behavior, habitat, and conservation status."
                },
                {
                    "name": "Field Reports",
                    "description": "Share your observations and experiences from the field."
                },
                {
                    "name": "Research & Science",
                    "description": "Scientific discussions, research questions, and methodology sharing."
                },
                {
                    "name": "Conservation Projects",
                    "description": "Discuss ongoing and upcoming conservation projects and initiatives."
                },
                {
                    "name": "Education & Outreach",
                    "description": "Topics related to conservation education and community outreach programs."
                },
                {
                    "name": "Wildlife Photography",
                    "description": "Share and discuss wildlife photography techniques, equipment, and ethics."
                }
            ]
            
            # Add forum categories to database
            categories_map = {}  # To store category IDs for creating threads
            for category_data in forum_categories:
                category = ForumCategory(**category_data)
                db.session.add(category)
                db.session.flush()  # To get the category ID
                categories_map[category.name] = category.id
            
            # Create forum threads and posts
            forum_content = [
                {
                    "category": "Conservation News",
                    "title": "New Marine Protected Area Established in Raja Ampat",
                    "content": "The Indonesian government has designated a new marine protected area in Raja Ampat, covering over 100,000 hectares of critical coral reef habitat. This is great news for marine conservation!",
                    "posts": [
                        "This is fantastic news! Raja Ampat has some of the highest marine biodiversity in the world. I've been diving there and the coral reefs are spectacular.",
                        "I wonder what specific protections will be implemented? Will there be no-take zones or just limited fishing?",
                        "According to the press release, there will be three different zones: a no-take zone covering about 30% of the area, a traditional use zone for local communities, and a sustainable use zone where certain activities are allowed with permits."
                    ]
                },
                {
                    "category": "Conservation News",
                    "title": "Orangutan Habitat Restoration Project Launched",
                    "content": "A major new initiative to restore degraded orangutan habitat in Borneo has been launched with international funding. The project aims to replant 10,000 hectares of forest over the next five years.",
                    "posts": [
                        "This is so important. I've been following the deforestation rates in Borneo and it's heartbreaking how much habitat has been lost.",
                        "What tree species are they planning to plant? It's important to restore the right food trees for orangutans.",
                        "Will this project also address the issue of palm oil plantations? It seems like restoration won't be effective if deforestation continues elsewhere."
                    ]
                },
                {
                    "category": "Species Discussion",
                    "title": "Komodo Dragon Population Trends",
                    "content": "I've been reading conflicting reports about Komodo dragon population trends. Some sources say numbers are stable, while others suggest they're declining. Does anyone have access to the most recent population surveys?",
                    "posts": [
                        "The most recent peer-reviewed study I've seen (published last year) estimated about 3,000 individuals across all islands, which is actually a slight increase from the previous survey.",
                        "It's important to note that the population is fragmented across several islands, so while the total number might be stable, some subpopulations could be at risk.",
                        "The bigger concerns seem to be habitat degradation and potential impacts of tourism, rather than direct population decline at the moment."
                    ]
                },
                {
                    "category": "Species Discussion",
                    "title": "Unusual Javan Rhino Behavior Observed",
                    "content": "During my recent field work in Ujung Kulon National Park, I observed some unusual social behavior in Javan rhinos that doesn't seem to be documented in the literature. Has anyone else noticed rhinos gathering in groups larger than 2-3 individuals?",
                    "posts": [
                        "This is fascinating! Javan rhinos are typically solitary except for mothers with calves. How many individuals did you observe together?",
                        "Was this near a water source? Sometimes seemingly social gatherings are just independent visits to a limited resource.",
                        "Could you share any photos or more details about the behavior? This could be important information for conservation management."
                    ]
                },
                {
                    "category": "Field Reports",
                    "title": "Sumatran Tiger Tracks in Kerinci Seblat",
                    "content": "Just returned from a monitoring trip in Kerinci Seblat National Park. We found fresh tiger tracks in three different locations, suggesting at least two different individuals based on paw size. Encouraging signs!",
                    "posts": [
                        "That's great news! Did you set up any camera traps to try to get visual confirmation?",
                        "Kerinci Seblat is one of the last strongholds for Sumatran tigers. Thanks for sharing this positive update.",
                        "Were there any signs of prey species in the same areas? Healthy prey populations are so important for tiger conservation."
                    ]
                },
                {
                    "category": "Field Reports",
                    "title": "Babirusa Sighting in North Sulawesi",
                    "content": "I was incredibly lucky to observe a male babirusa in the wild yesterday near Tangkoko Nature Reserve. It was feeding peacefully for about 10 minutes before disappearing into the undergrowth. Attaching coordinates for those interested.",
                    "posts": [
                        "Wow, that's a rare sighting! Babirusas are so elusive. Did you manage to get any photos?",
                        "Thanks for sharing the coordinates. I'll add this to our sightings database for North Sulawesi. This helps build our understanding of their current range.",
                        "Was it in primary forest or more disturbed habitat? There's been some research suggesting they're more adaptable than previously thought."
                    ]
                },
                {
                    "category": "Research & Science",
                    "title": "eDNA Methods for Marine Species Monitoring",
                    "content": "I'm planning a research project using environmental DNA (eDNA) sampling to monitor marine species in the Coral Triangle. Has anyone here used these techniques in tropical marine environments? Any tips or protocols to share?",
                    "posts": [
                        "I've used eDNA for reef fish surveys in Raja Ampat. The biggest challenge was preservation of samples given the remote location and hot climate. I'd recommend bringing plenty of silica gel and possibly a portable freezer.",
                        "Check out the recent paper by Wong et al. (2024) in Marine Ecology Progress Series - they developed an optimized protocol specifically for tropical marine environments.",
                        "One thing to consider is the tidal cycle when sampling. We found significantly different results between high and low tide samples in mangrove areas."
                    ]
                },
                {
                    "category": "Research & Science",
                    "title": "Statistical Analysis for Camera Trap Data",
                    "content": "I'm struggling with the statistical analysis of my camera trap data for terrestrial mammals in Sumatra. I have presence/absence data across 50 sites with different habitat variables. What's the best approach for analyzing habitat associations?",
                    "posts": [
                        "Occupancy modeling would be perfect for this type of data. Check out the 'unmarked' package in R, which has good functions for this kind of analysis.",
                        "How are you handling imperfect detection? That's a major consideration with camera trap data and will affect your habitat association results.",
                        "I recently published a study with similar data. I used a hierarchical Bayesian approach that worked well for teasing apart detection vs. occupancy covariates. Happy to share my code if helpful."
                    ]
                },
                {
                    "category": "Conservation Projects",
                    "title": "Community-Based Patrol Program Seeking Volunteers",
                    "content": "Our NGO is expanding our community-based forest patrol program in Central Kalimantan. We're looking for volunteers with experience in wildlife monitoring, community engagement, or forestry to help train local patrol teams. Program runs for 3-month commitments.",
                    "posts": [
                        "This sounds like a great initiative! Can you share more details about what qualifications you're looking for and the application process?",
                        "I volunteered with a similar program in Aceh last year. It was an incredible experience. Happy to chat with anyone considering this opportunity.",
                        "Are you providing any language training? My concern would be communication with local communities if volunteers don't speak Indonesian or the local dialect."
                    ]
                },
                {
                    "category": "Conservation Projects",
                    "title": "Sea Turtle Nest Protection Results",
                    "content": "Our sea turtle nest protection project on Bali's east coast just completed its fifth year. We're excited to report a 73% increase in successful leatherback turtle nests compared to our baseline data. Community engagement has been key to this success.",
                    "posts": [
                        "Congratulations! That's a significant achievement. How many local community members are involved in the project now?",
                        "I'd be interested to know more about your community engagement approach. What incentives or benefits do local communities receive for participating?",
                        "Have you observed any changes in local attitudes toward conservation over the five years of the project? This kind of data is so valuable for other community conservation initiatives."
                    ]
                },
                {
                    "category": "Education & Outreach",
                    "title": "Developing Educational Materials for Rural Schools",
                    "content": "I'm developing conservation education materials for elementary schools in rural Indonesia. Looking for advice on making materials engaging and culturally appropriate while conveying important conservation concepts.",
                    "posts": [
                        "I've found that using local folktales and traditional stories as a framework for introducing conservation concepts works really well. It connects to cultural values the children already understand.",
                        "Consider focusing on local flagship species that children might actually encounter. Sometimes conservation education uses tigers and elephants even in areas where these aren't relevant to local ecosystems.",
                        "Make sure to include plenty of interactive elements - games, role-playing activities, art projects. These are more effective than lecture-style teaching, especially for younger children."
                    ]
                },
                {
                    "category": "Education & Outreach",
                    "title": "Conservation Radio Program Success Story",
                    "content": "Just wanted to share that our weekly conservation radio program has now been running for one year in West Papua. Reaching remote communities with limited internet access has been incredibly effective for spreading conservation awareness.",
                    "posts": [
                        "This is fantastic! Radio is so overlooked as a communication tool these days, but it's perfect for reaching remote communities. What kind of content seems to be most popular with listeners?",
                        "Have you considered creating podcast versions of the programs for areas with better internet access? Could expand your reach even further.",
                        "Would you be willing to share your program format and some episode outlines? I'm interested in starting something similar in Sulawesi."
                    ]
                },
                {
                    "category": "Wildlife Photography",
                    "title": "Ethical Wildlife Photography Guidelines",
                    "content": "After witnessing some concerning behavior from photographers at a popular bird watching site, I think we need to discuss ethical wildlife photography practices. What guidelines do you follow to ensure you're not disturbing the animals you photograph?",
                    "posts": [
                        "Great topic! My main rule is: if the animal changes its behavior because of my presence, I'm too close and need to back off.",
                        "I never use calls or playback to attract birds for photography. It can disrupt breeding behaviors and waste birds' energy when they respond thinking it's a territorial rival.",
                        "I think tour operators have a responsibility here too. I've seen guides encouraging photographers to get closer and closer for 'the perfect shot,' placing unnecessary stress on wildlife."
                    ]
                },
                {
                    "category": "Wildlife Photography",
                    "title": "Camera Settings for Rainforest Photography",
                    "content": "I'm planning my first photography trip to the Indonesian rainforest and struggling with camera settings for the low light conditions. Any recommendations from experienced rainforest photographers?",
                    "posts": [
                        "Low light is definitely the biggest challenge! I recommend a fast lens (f/2.8 or faster) and be prepared to increase your ISO. Modern cameras handle high ISO much better than older models.",
                        "Consider bringing a monopod rather than a tripod - they're much easier to maneuver in dense forest and still help with stability for slower shutter speeds.",
                        "Don't forget to protect your gear from humidity. Bring plenty of silica gel packets and consider a waterproof camera cover even if it's not raining - the humidity can be intense."
                    ]
                },
                {
                    "category": "Conservation News",
                    "title": "New Study on Plastic Pollution in Indonesian Waters",
                    "content": "A new study published this week in Marine Pollution Bulletin shows that plastic pollution in Indonesian waters has increased by 30% over the past five years, with serious implications for marine life.",
                    "posts": [
                        "This is unfortunately not surprising, but still very concerning. Was there any information about the main sources of this plastic? Is it local or coming from other countries?",
                        "I've been involved in beach cleanups in Bali, and we've noticed a significant increase in certain types of plastic packaging. Better waste management infrastructure is urgently needed.",
                        "Did the study mention impacts on specific marine species? I'm particularly concerned about sea turtles mistaking plastic bags for jellyfish."
                    ]
                },
                {
                    "category": "Species Discussion",
                    "title": "Banteng Conservation Status Question",
                    "content": "I'm trying to understand more about the conservation status of banteng in Indonesia. The IUCN lists them as Endangered, but I've heard populations might be stable in some protected areas. Does anyone have current information?",
                    "posts": [
                        "I was involved in a banteng survey in Baluran National Park last year. The population there seems stable at around 35-40 individuals, but that's a very small, isolated population.",
                        "The main threats continue to be habitat loss and hybridization with domestic cattle. Even if some populations are stable, genetic integrity is a serious concern.",
                        "There's been some success with banteng conservation in Alas Purwo National Park. Their management approach might be a good model for other protected areas."
                    ]
                }
            ]
            
            # Add forum threads and posts to database
            for thread_data in forum_content:
                # Create the thread
                thread = ForumThread(
                    title=thread_data["title"],
                    content=thread_data["content"],
                    author_id=teacher.id,
                    category_id=categories_map[thread_data["category"]]
                )
                db.session.add(thread)
                db.session.flush()  # To get the thread ID
                
                # Add posts to the thread
                for post_content in thread_data["posts"]:
                    post = ForumPost(
                        content=post_content,
                        author_id=teacher.id,
                        thread_id=thread.id
                    )
                    db.session.add(post)
            
            try:
                db.session.commit()
                app.logger.info("Sample data created successfully")
            except Exception as commit_error:
                app.logger.error(f"Error committing sample data: {str(commit_error)}")
                db.session.rollback()
        else:
            app.logger.info("Database already contains data, skipping sample data creation")
    except Exception as e:
        app.logger.error(f"Error creating sample data: {str(e)}")
        db.session.rollback()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {error}')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Initialize database and register blueprints
with app.app_context():
    try:
        # First drop all tables to ensure clean database
        app.logger.info("Dropping any existing tables...")
        db.drop_all()
        
        # Create all tables
        app.logger.info("Creating database tables...")
        db.create_all()
        app.logger.info("Database tables created successfully")

        # Create basic sample data
        create_sample_data()
        
        # Import and create enhanced sample data
        try:
            from scripts.enhanced_data import create_enhanced_data
            app.logger.info("Running enhanced data creation...")
            create_enhanced_data()
            app.logger.info("Enhanced data creation completed")
        except Exception as enhanced_data_error:
            app.logger.error(f"Error creating enhanced data: {str(enhanced_data_error)}")
            app.logger.warning("Proceeding with basic sample data only")

        # Import and register blueprints
        from blueprints.auth import auth
        from blueprints.main import main
        from blueprints.species import species
        from blueprints.forum import forum
        from blueprints.library import library
        from blueprints.programs import programs
        from blueprints.admin import admin_bp
        from blueprints.progress import progress

        # Register blueprints with URL prefixes
        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(main)
        app.register_blueprint(species, url_prefix='/species')
        app.register_blueprint(forum, url_prefix='/forum')
        app.register_blueprint(library, url_prefix='/library')
        app.register_blueprint(programs, url_prefix='/programs')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(progress, url_prefix='/progress')

        app.logger.info("All blueprints registered successfully")
        
        # Print login credentials for testing (helpful for users)
        app.logger.info("==== SAMPLE LOGIN CREDENTIALS ====")
        app.logger.info("Teacher: email='teacher@test.com', password='password123'")
        app.logger.info("Community: email='community@example.com', password='password123'")
        app.logger.info("Student: email='student1@example.com', password='password123'")
        app.logger.info("Admin: email='admin@komodo.com', password='admin123' (Full database control)")
        app.logger.info("================================")

    except Exception as e:
        app.logger.error(f"Error during app initialization: {str(e)}")
        raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)