"""
Enhanced data initialization script for Komodo Hub.
This script adds a comprehensive set of sample data for testing and demonstration.
"""

import sys
import os
import random
from datetime import datetime, timedelta
import logging

# Add the parent directory to the path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import (
    User, Species, LibraryResource, ForumCategory, ForumThread, ForumPost,
    ConservationProgram, SpeciesSighting, AchievementLevel, Achievement,
    SpeciesIdentificationChallenge
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_enhanced_data():
    """Create a comprehensive set of sample data for demonstration purposes."""
    
    # Make sure we're using the same database path as the main app
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///komodo.db"
    
    with app.app_context():
        try:
            # Always create enhanced data (run on every startup)
            logger.info("Creating fresh enhanced data...")
                
            logger.info("Starting enhanced data creation...")
            
            # Create additional users with different roles
            users = create_sample_users()
            
            # Create species data
            species_list = create_sample_species(users)
            
            # Create forum categories and threads
            create_sample_forum(users)
            
            # Create library resources
            create_sample_resources(users)
            
            # Create conservation programs
            create_sample_programs(users)
            
            # Create species sightings
            create_sample_sightings(users, species_list)
            
            # Create achievements and challenges
            create_sample_gamification(users, species_list)
            
            logger.info("Enhanced data creation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error creating enhanced data: {str(e)}")
            db.session.rollback()
            raise

def create_sample_users():
    """Create sample users with different roles."""
    logger.info("Creating sample users...")
    
    users = []
    
    # Get existing users for sample data
    existing_users = User.query.all()
    for user in existing_users:
        users.append(user)
        logger.info(f"Using existing user: {user.username} ({user.email})")
    
    # If no existing users, this won't run since we populate in app.py
    if not users:
        # Create additional community members with different emails
        for i in range(2, 4):
            member = User(
                username=f"community{i}",
                email=f"community{i}@example.com",
                role="community"
            )
            member.set_password("password123")
            db.session.add(member)
            users.append(member)
        
        # Create additional teacher
        teacher = User(
            username="wildlife_prof",
            email="teacher_wildlife@example.com",
            role="teacher"
        )
        teacher.set_password("password123")
        db.session.add(teacher)
        users.append(teacher)
    
    # Create additional community members with different emails only if not already existing
    existing_emails = [user.email for user in users]
    for i in range(4, 6):  # Use higher numbers to avoid conflicts
        email = f"community{i}@example.com"
        if email not in existing_emails:
            member = User(
                username=f"community{i}",
                email=email,
                role="community"
            )
            member.set_password("password123")
            db.session.add(member)
            users.append(member)
    
    db.session.flush()
    logger.info(f"Created {len(users)} sample users")
    return users

def create_sample_species(users):
    """Create a comprehensive set of sample species."""
    logger.info("Creating sample species...")
    
    species_data = [
        {
            "name": "Komodo Dragon",
            "scientific_name": "Varanus komodoensis",
            "description": "The largest living species of lizard, found in Indonesian islands. Can grow up to 3 meters long and weigh over 70 kg.",
            "conservation_status": "EN",
            "habitat": "Tropical savanna forests",
            "threats": "Habitat loss, human conflict, poaching",
            "population": 3000
        },
        {
            "name": "Sumatran Tiger",
            "scientific_name": "Panthera tigris sumatrae",
            "description": "A rare tiger subspecies native to the Indonesian island of Sumatra, with distinctive dark stripes and a reddish-orange coat.",
            "conservation_status": "CR",
            "habitat": "Tropical forests",
            "threats": "Poaching, deforestation, human-wildlife conflict",
            "population": 400
        },
        {
            "name": "Javan Rhino",
            "scientific_name": "Rhinoceros sondaicus",
            "description": "One of the most endangered large mammals in the world, with only a small population remaining in Indonesia's Ujung Kulon National Park.",
            "conservation_status": "CR",
            "habitat": "Lowland tropical rainforests",
            "threats": "Habitat loss, poaching, small population size",
            "population": 72
        },
        {
            "name": "Sumatran Orangutan",
            "scientific_name": "Pongo abelii",
            "description": "A critically endangered species of great ape native to Indonesia's Sumatra island, known for their intelligence and distinctive reddish fur.",
            "conservation_status": "CR",
            "habitat": "Tropical rainforests",
            "threats": "Deforestation, palm oil plantations, illegal pet trade",
            "population": 14000
        },
        {
            "name": "Bali Starling",
            "scientific_name": "Leucopsar rothschildi",
            "description": "A beautiful white bird endemic to Bali, Indonesia, with blue skin around the eyes and a long, drooping crest.",
            "conservation_status": "CR",
            "habitat": "Dry, open forests",
            "threats": "Illegal capture for pet trade, habitat loss",
            "population": 100
        },
        {
            "name": "Sumatran Elephant",
            "scientific_name": "Elephas maximus sumatranus",
            "description": "A subspecies of the Asian elephant native to Sumatra, recognizable by their smaller size and relatively larger ears.",
            "conservation_status": "CR",
            "habitat": "Lowland forests",
            "threats": "Habitat loss, human-elephant conflict, poaching",
            "population": 2400
        },
        {
            "name": "Banteng",
            "scientific_name": "Bos javanicus",
            "description": "A species of wild cattle found in Southeast Asia, with a distinctive white patch on the hindquarters.",
            "conservation_status": "EN",
            "habitat": "Dry, deciduous forests and grasslands",
            "threats": "Hunting, habitat loss, hybridization with domestic cattle",
            "population": 8000
        },
        {
            "name": "Sumatran Rhinoceros",
            "scientific_name": "Dicerorhinus sumatrensis",
            "description": "The smallest of all rhino species and the only Asian rhino with two horns, covered with long hair.",
            "conservation_status": "CR",
            "habitat": "Dense mountain forests",
            "threats": "Poaching, habitat loss, small population",
            "population": 80
        },
        {
            "name": "Malayan Tapir",
            "scientific_name": "Tapirus indicus",
            "description": "The largest of the five tapir species, characterized by their distinctive black and white pattern resembling an oreo cookie.",
            "conservation_status": "EN",
            "habitat": "Tropical forests",
            "threats": "Habitat destruction, hunting, road kills",
            "population": 2500
        },
        {
            "name": "Clouded Leopard",
            "scientific_name": "Neofelis nebulosa",
            "description": "A wild cat with distinctive cloud-like patterns on its coat and exceptionally long canine teeth.",
            "conservation_status": "VU",
            "habitat": "Tropical forests",
            "threats": "Deforestation, poaching for fur and bones",
            "population": 10000
        },
        {
            "name": "Proboscis Monkey",
            "scientific_name": "Nasalis larvatus",
            "description": "An endemic monkey species to Borneo, known for the male's large pendulous nose used to attract females.",
            "conservation_status": "EN",
            "habitat": "Mangrove, riverine, and swamp forests",
            "threats": "Habitat loss, hunting",
            "population": 7000
        },
        {
            "name": "Sunda Pangolin",
            "scientific_name": "Manis javanica",
            "description": "A critically endangered mammal covered in protective scales, hunted for its meat and scales used in traditional medicine.",
            "conservation_status": "CR",
            "habitat": "Secondary, disturbed forests",
            "threats": "Illegal wildlife trade, habitat loss",
            "population": 1000
        },
        {
            "name": "Babirusa",
            "scientific_name": "Babyrousa babyrussa",
            "description": "An unusual pig species with tusks that grow upward through the snout and curve backward toward the forehead.",
            "conservation_status": "VU",
            "habitat": "Tropical forests, riverbanks",
            "threats": "Hunting, habitat loss",
            "population": 4000
        },
        {
            "name": "Anoa",
            "scientific_name": "Bubalus depressicornis",
            "description": "A small, forest-dwelling buffalo endemic to Sulawesi, with straight horns and a dark brown to black coat.",
            "conservation_status": "EN",
            "habitat": "Lowland and mountain forests",
            "threats": "Hunting, habitat loss",
            "population": 5000
        },
        {
            "name": "Javan Hawk-eagle",
            "scientific_name": "Nisaetus bartelsi",
            "description": "A medium-large bird of prey endemic to Java, recognized as Indonesia's national bird.",
            "conservation_status": "EN",
            "habitat": "Tropical forests",
            "threats": "Habitat loss, capture for pet trade",
            "population": 600
        },
        {
            "name": "Dugong",
            "scientific_name": "Dugong dugon",
            "description": "A marine mammal related to manatees, feeding exclusively on seagrass in coastal waters around Indonesia.",
            "conservation_status": "VU",
            "habitat": "Shallow coastal waters with seagrass beds",
            "threats": "Hunting, boat strikes, habitat degradation",
            "population": 1000
        },
        {
            "name": "Irrawaddy Dolphin",
            "scientific_name": "Orcaella brevirostris",
            "description": "A small dolphin with a rounded head and no beak, found in coastal areas and major river systems.",
            "conservation_status": "EN",
            "habitat": "Coastal, brackish and freshwater systems",
            "threats": "Bycatch in fishing gear, habitat degradation",
            "population": 7500
        },
        {
            "name": "Green Turtle",
            "scientific_name": "Chelonia mydas",
            "description": "A large sea turtle with a heart-shaped shell, named for the greenish color of its fat rather than its shell.",
            "conservation_status": "EN",
            "habitat": "Tropical and subtropical waters worldwide",
            "threats": "Egg collection, hunting, plastic pollution, climate change",
            "population": 85000
        },
        {
            "name": "Leatherback Sea Turtle",
            "scientific_name": "Dermochelys coriacea",
            "description": "The largest of all living turtles, lacking a bony shell and instead covered with leathery skin.",
            "conservation_status": "CR",
            "habitat": "Open ocean, nests on tropical beaches",
            "threats": "Egg collection, bycatch, plastic pollution",
            "population": 26000
        },
        {
            "name": "Sulawesi Bear Cuscus",
            "scientific_name": "Ailurops ursinus",
            "description": "A large marsupial with thick fur and a prehensile tail, endemic to Sulawesi.",
            "conservation_status": "VU",
            "habitat": "Tropical forests",
            "threats": "Hunting, habitat loss",
            "population": 9000
        },
        {
            "name": "Black Crested Macaque",
            "scientific_name": "Macaca nigra",
            "description": "A monkey species endemic to Sulawesi, with an entirely jet-black body and distinctive crest of hair.",
            "conservation_status": "CR",
            "habitat": "Tropical rainforests",
            "threats": "Hunting for bushmeat, habitat loss, pet trade",
            "population": 5000
        },
        {
            "name": "Sumatran Laughingthrush",
            "scientific_name": "Garrulax bicolor",
            "description": "A striking bird with pure white plumage and a black face mask, known for its beautiful song.",
            "conservation_status": "EN",
            "habitat": "Mountain forests",
            "threats": "Capture for cage bird trade, habitat loss",
            "population": 2500
        },
        {
            "name": "Wallace's Flying Frog",
            "scientific_name": "Rhacophorus nigropalmatus",
            "description": "A large tree frog with webbed feet that allow it to glide through the air when jumping from trees.",
            "conservation_status": "LC",
            "habitat": "Tropical rainforests",
            "threats": "Habitat loss, climate change",
            "population": 10000
        },
        {
            "name": "Bornean Orangutan",
            "scientific_name": "Pongo pygmaeus",
            "description": "A critically endangered great ape native to Borneo, with distinctive red-orange hair and slower movements than its Sumatran cousin.",
            "conservation_status": "CR",
            "habitat": "Tropical and subtropical moist broadleaf forests",
            "threats": "Deforestation, palm oil plantations, illegal hunting",
            "population": 104700
        }
    ]
    
    species_list = []
    for data in species_data:
        # Assign a random creator from the users list
        creator = random.choice(users)
        species = Species(
            name=data["name"],
            scientific_name=data["scientific_name"],
            description=data["description"],
            conservation_status=data["conservation_status"],
            habitat=data["habitat"],
            threats=data["threats"],
            population=data["population"],
            created_by_id=creator.id
        )
        db.session.add(species)
        species_list.append(species)
    
    db.session.flush()
    logger.info(f"Created {len(species_list)} sample species")
    return species_list

def create_sample_forum(users):
    """Create sample forum categories, threads, and posts."""
    logger.info("Creating sample forum content...")
    
    # Create forum categories
    categories = [
        {
            "name": "Conservation News",
            "description": "Discuss the latest news and developments in wildlife conservation."
        },
        {
            "name": "Species Identification Help",
            "description": "Get help identifying species you've encountered in the wild."
        },
        {
            "name": "Research & Science",
            "description": "Share and discuss scientific research related to Indonesian wildlife."
        },
        {
            "name": "Field Techniques",
            "description": "Tips and methods for wildlife observation and research in the field."
        },
        {
            "name": "Conservation Programs",
            "description": "Information and discussions about active conservation programs."
        }
    ]
    
    category_objects = []
    for data in categories:
        category = ForumCategory(
            name=data["name"],
            description=data["description"]
        )
        db.session.add(category)
        category_objects.append(category)
    
    db.session.flush()
    
    # Create threads and posts
    threads_data = [
        {
            "category_index": 0,
            "title": "New protection measures announced for Komodo National Park",
            "content": "The Indonesian government has announced new protection measures for Komodo National Park, including increased ranger patrols and stricter visitor regulations. What do you think about these changes?",
            "post_count": 5
        },
        {
            "category_index": 0,
            "title": "Population of Javan Rhinos shows slight increase",
            "content": "Recent surveys indicate a small but promising increase in the Javan Rhino population in Ujung Kulon National Park. This is great news for conservation efforts!",
            "post_count": 3
        },
        {
            "category_index": 1,
            "title": "Help identifying this frog species from West Java",
            "content": "I encountered this frog during a recent hiking trip in West Java. It was bright green with unusual red markings on its back. Any ideas what species it might be?",
            "post_count": 4
        },
        {
            "category_index": 2,
            "title": "New research on orangutan tool use published",
            "content": "A fascinating new study on tool use among wild orangutans in Sumatra has been published in Nature. The researchers documented 37 different tools used by the apes for various purposes.",
            "post_count": 6
        },
        {
            "category_index": 3,
            "title": "Best camera traps for rainforest environments?",
            "content": "I'm planning a field study in Sulawesi's rainforests and need recommendations for reliable camera traps that can withstand the humid conditions. Any suggestions from those with experience?",
            "post_count": 7
        },
        {
            "category_index": 4,
            "title": "Volunteer opportunities for sea turtle conservation in Indonesia",
            "content": "I'm looking for information about volunteer programs focused on sea turtle conservation in Indonesia. Has anyone participated in such programs and can share their experiences?",
            "post_count": 5
        },
        {
            "category_index": 2,
            "title": "Genetic diversity in isolated Sumatran tiger populations",
            "content": "I'm starting a research project on genetic diversity in isolated Sumatran tiger populations. Looking for collaborators or suggestions on methodology.",
            "post_count": 3
        },
        {
            "category_index": 1,
            "title": "Strange bird spotted in Bali - need help with ID",
            "content": "While birdwatching near Ubud, I spotted this unusual bird with bright blue plumage and a distinctive call. Photos attached. Any ornithologists who can help identify it?",
            "post_count": 4
        }
    ]
    
    for thread_data in threads_data:
        category = category_objects[thread_data["category_index"]]
        author = random.choice(users)
        
        thread = ForumThread(
            title=thread_data["title"],
            content=thread_data["content"],
            author_id=author.id,
            category_id=category.id,
            is_pinned=random.random() < 0.2,  # 20% chance of being pinned
            view_count=random.randint(5, 100)
        )
        db.session.add(thread)
        db.session.flush()
        
        # Create posts (replies) for this thread
        for i in range(thread_data["post_count"]):
            post_author = random.choice(users)
            
            responses = [
                "This is really interesting information, thanks for sharing!",
                "I've observed similar behaviors in my field studies.",
                "Have you considered looking into the related research by Dr. Wong at UGM?",
                "I disagree with some points here. Recent studies suggest otherwise.",
                "Great post! This aligns perfectly with what we've been seeing in Sumatra.",
                "Could you provide more details about your methodology?",
                "This species is particularly vulnerable to climate change impacts.",
                "I've been working with this species for 5 years and can confirm these findings.",
                "What conservation implications do you see from these observations?",
                "Has anyone tried implementing these techniques in different regions?",
                "The government should allocate more resources to protecting this species.",
                "Thanks for raising awareness about this important issue!"
            ]
            
            post = ForumPost(
                content=random.choice(responses),
                author_id=post_author.id,
                thread_id=thread.id,
                upvotes_count=random.randint(0, 15)
            )
            db.session.add(post)
    
    db.session.flush()
    logger.info(f"Created {len(category_objects)} forum categories and {len(threads_data)} threads with replies")

def create_sample_resources(users):
    """Create sample library resources."""
    logger.info("Creating sample library resources...")
    
    resources_data = [
        {
            "title": "Conservation Basics",
            "content": "An introduction to wildlife conservation principles and practices, covering the fundamental concepts of biodiversity preservation, habitat protection, and sustainable resource management.",
            "resource_type": "article"
        },
        {
            "title": "Field Research Guide",
            "content": "Best practices for conducting wildlife field research, including observation techniques, data collection methods, and ethical considerations when working with animals in their natural habitats.",
            "resource_type": "guide"
        },
        {
            "title": "Komodo Dragon Biology",
            "content": "A comprehensive overview of Komodo dragon biology, behavior, and ecology. Includes information on their unique hunting techniques, reproductive strategies, and evolutionary history.",
            "resource_type": "research"
        },
        {
            "title": "Indonesian Rainforest Ecosystems",
            "content": "An exploration of the diverse rainforest ecosystems found across the Indonesian archipelago, highlighting their unique flora and fauna and the conservation challenges they face.",
            "resource_type": "article"
        },
        {
            "title": "Wildlife Photography Ethics",
            "content": "Ethical guidelines for wildlife photography, ensuring that photographers minimize their impact on animal behavior and habitats while capturing compelling images.",
            "resource_type": "guide"
        },
        {
            "title": "Orangutan Conservation Status Report",
            "content": "A detailed report on the current conservation status of orangutans in Sumatra and Borneo, including population trends, threats, and ongoing conservation initiatives.",
            "resource_type": "research"
        },
        {
            "title": "Bird Identification in Java",
            "content": "A practical guide to identifying common and rare bird species found on the island of Java, with descriptions, habitat information, and behavioral cues.",
            "resource_type": "guide"
        },
        {
            "title": "Marine Conservation Challenges",
            "content": "An overview of the unique challenges facing marine conservation efforts in Indonesia's coral reef ecosystems, including climate change impacts, fishing practices, and pollution.",
            "resource_type": "article"
        },
        {
            "title": "Traditional Ecological Knowledge",
            "content": "The importance of incorporating traditional ecological knowledge from indigenous communities into modern conservation practices in Indonesia.",
            "resource_type": "research"
        },
        {
            "title": "Wildlife Tracking Techniques",
            "content": "A guide to various wildlife tracking techniques, from traditional skills to modern GPS and satellite technologies used in conservation research.",
            "resource_type": "guide"
        },
        {
            "title": "Conservation Genetics Primer",
            "content": "An introduction to the field of conservation genetics and its applications in preserving endangered species through understanding genetic diversity and population structure.",
            "resource_type": "research"
        },
        {
            "title": "Climate Change Impacts on Indonesian Biodiversity",
            "content": "Research findings on how climate change is affecting Indonesia's unique biodiversity, with case studies from various ecosystems across the archipelago.",
            "resource_type": "research"
        },
        {
            "title": "Community-Based Conservation Success Stories",
            "content": "Examples of successful community-based conservation initiatives from across Indonesia, highlighting how local involvement can lead to sustainable outcomes.",
            "resource_type": "article"
        },
        {
            "title": "Wildlife Rehabilitation Best Practices",
            "content": "Guidelines for the rehabilitation and release of injured or orphaned wildlife, with specific considerations for Indonesian species.",
            "resource_type": "guide"
        },
        {
            "title": "Ecotourism Development Guide",
            "content": "A practical guide for developing ecotourism initiatives that benefit both local communities and wildlife conservation efforts in Indonesia.",
            "resource_type": "guide"
        }
    ]
    
    for data in resources_data:
        author = random.choice(users)
        
        resource = LibraryResource(
            title=data["title"],
            content=data["content"],
            resource_type=data["resource_type"],
            author_id=author.id,
            is_public=random.random() < 0.8  # 80% chance of being public
        )
        db.session.add(resource)
    
    db.session.flush()
    logger.info(f"Created {len(resources_data)} library resources")

def create_sample_programs(users):
    """Create sample conservation programs."""
    logger.info("Creating sample conservation programs...")
    
    programs_data = [
        {
            "title": "Javan Rhino Protection Initiative",
            "description": "A comprehensive program aimed at protecting the last remaining population of Javan rhinos in Ujung Kulon National Park through increased security measures, habitat management, and genetic research.",
            "location": "Ujung Kulon National Park, Java"
        },
        {
            "title": "Sumatran Tiger Corridor Project",
            "description": "Establishing and protecting wildlife corridors between fragmented forest habitats to allow Sumatran tigers to move safely between protected areas and maintain genetic diversity.",
            "location": "Sumatra"
        },
        {
            "title": "Bali Starling Breeding Program",
            "description": "A captive breeding and release program aimed at increasing the wild population of the critically endangered Bali starling in its native habitat.",
            "location": "Bali"
        },
        {
            "title": "Coral Reef Restoration Project",
            "description": "Restoring damaged coral reefs through innovative transplantation techniques and community-based protection measures in marine protected areas across Indonesia.",
            "location": "Raja Ampat, West Papua"
        },
        {
            "title": "Orangutan Habitat Protection",
            "description": "Working with local communities and palm oil companies to protect remaining orangutan habitat through sustainable land use practices and the creation of new protected areas.",
            "location": "Kalimantan and Sumatra"
        },
        {
            "title": "Sulawesi Endemic Species Conservation",
            "description": "A multi-species conservation program focused on protecting Sulawesi's unique endemic mammals, including the anoa, babirusa, and macaques through research and community engagement.",
            "location": "Sulawesi"
        },
        {
            "title": "Sea Turtle Nesting Beach Protection",
            "description": "Protecting important sea turtle nesting beaches from development, light pollution, and egg poaching through community patrol teams and educational initiatives.",
            "location": "Various coastal areas of Indonesia"
        },
        {
            "title": "Mangrove Restoration Initiative",
            "description": "Restoring degraded mangrove ecosystems to improve coastal protection, carbon sequestration, and habitat for numerous marine and terrestrial species.",
            "location": "East Kalimantan"
        }
    ]
    
    for data in programs_data:
        # Select a coordinator (teacher or community member only)
        potential_coordinators = [u for u in users if u.role in ['teacher', 'community']]
        coordinator = random.choice(potential_coordinators)
        
        # Create dates
        start_date = datetime.now() - timedelta(days=random.randint(0, 60))
        end_date = start_date + timedelta(days=random.randint(180, 365))
        
        program = ConservationProgram(
            title=data["title"],
            description=data["description"],
            location=data["location"],
            start_date=start_date,
            end_date=end_date,
            coordinator_id=coordinator.id,
            participant_count=random.randint(5, 50)
        )
        db.session.add(program)
    
    db.session.flush()
    logger.info(f"Created {len(programs_data)} conservation programs")

def create_sample_sightings(users, species_list):
    """Create sample species sightings."""
    logger.info("Creating sample species sightings...")
    
    locations = [
        "Komodo National Park, East Nusa Tenggara",
        "Ujung Kulon National Park, West Java",
        "Gunung Leuser National Park, Aceh",
        "Tanjung Puting National Park, Central Kalimantan",
        "Wakatobi National Park, Southeast Sulawesi",
        "Bunaken National Park, North Sulawesi",
        "Bali Barat National Park, Bali",
        "Way Kambas National Park, Lampung",
        "Raja Ampat, West Papua",
        "Kerinci Seblat National Park, Sumatra",
        "Lore Lindu National Park, Central Sulawesi",
        "Bukit Barisan Selatan National Park, Lampung",
        "Gunung Palung National Park, West Kalimantan",
        "Wasur National Park, Papua",
        "Sembilang National Park, South Sumatra"
    ]
    
    sightings_count = 50  # Number of sightings to create
    
    for i in range(sightings_count):
        species = random.choice(species_list)
        observer = random.choice(users)
        location = random.choice(locations)
        
        sighting_date = datetime.now() - timedelta(days=random.randint(1, 180))
        
        descriptions = [
            f"Observed a {species.name} in its natural habitat, displaying typical feeding behavior.",
            f"Sighted a {species.name} with offspring, suggesting successful breeding in this area.",
            f"Encountered a {species.name} during a night survey, showing interesting nocturnal behavior.",
            f"Briefly glimpsed a {species.name} crossing a trail in the early morning.",
            f"Documented a {species.name} in an area where it hasn't been reported before, potentially expanding its known range.",
            f"Watched a group of {species.name} for approximately 30 minutes, noting social interactions.",
            f"Found evidence of {species.name} activity, including tracks and feeding signs.",
            f"Photographed a {species.name} in an unusual habitat, possibly due to seasonal movements."
        ]
        
        sighting = SpeciesSighting(
            species_id=species.id,
            user_id=observer.id,
            sighting_date=sighting_date,
            location=location,
            description=random.choice(descriptions),
            latitude=random.uniform(-8.0, -1.0),
            longitude=random.uniform(109.0, 125.0),
            status=random.choice(['pending', 'confirmed', 'confirmed', 'confirmed']),  # Bias toward confirmed
            likes_count=random.randint(0, 25),
            comments_count=random.randint(0, 10)
        )
        db.session.add(sighting)
    
    db.session.flush()
    logger.info(f"Created {sightings_count} species sightings")

def create_sample_gamification(users, species_list):
    """Create sample achievements and species identification challenges."""
    logger.info("Creating sample gamification elements...")
    
    # Create achievements
    achievements_data = [
        {
            "title": "Wildlife Observer",
            "description": "Report your first wildlife sighting",
            "category": "sightings",
            "points": 10
        },
        {
            "title": "Conservation Scholar",
            "description": "Read 5 educational resources in the library",
            "category": "education",
            "points": 15
        },
        {
            "title": "Community Contributor",
            "description": "Create your first forum post",
            "category": "community",
            "points": 10
        },
        {
            "title": "Species Expert",
            "description": "Correctly identify 10 different species",
            "category": "identification",
            "points": 20
        },
        {
            "title": "Conservation Volunteer",
            "description": "Participate in a conservation program",
            "category": "conservation",
            "points": 25
        }
    ]
    
    achievement_objects = []
    for data in achievements_data:
        achievement = Achievement(
            user_id=random.choice(users).id,
            title=data["title"],
            description=data["description"],
            category=data["category"],
            points=data["points"],
            badge_image=f"badges/{data['category']}.svg"
        )
        db.session.add(achievement)
        achievement_objects.append(achievement)
    
    db.session.flush()
    
    # Create species identification challenges
    challenge_count = 15
    for i in range(challenge_count):
        species = random.choice(species_list)
        
        difficulty = random.choice(['easy', 'medium', 'hard'])
        points = {'easy': 5, 'medium': 10, 'hard': 15}[difficulty]
        
        questions = [
            f"Identify this {species.name} from the image",
            f"What is the conservation status of the {species.name}?",
            f"Where is the primary habitat of the {species.name}?",
            f"What is the scientific name of the {species.name}?",
            f"What is the main threat facing the {species.name} in the wild?"
        ]
        
        challenge = SpeciesIdentificationChallenge(
            species_id=species.id,
            difficulty=difficulty,
            question_text=random.choice(questions),
            correct_answer=species.name,
            wrong_options="[\"Wrong Option 1\", \"Wrong Option 2\", \"Wrong Option 3\"]",
            hint=f"This species is found in {species.habitat}",
            points=points
        )
        db.session.add(challenge)
    
    db.session.flush()
    logger.info(f"Created {len(achievements_data)} achievements and {challenge_count} identification challenges")

if __name__ == "__main__":
    create_enhanced_data()