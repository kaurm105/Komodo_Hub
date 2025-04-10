from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Species, EducationalResource, ConservationProgram
from app import app, db
import logging

main = Blueprint('main', __name__)

@main.route('/')
def landing():
    """Landing page route - accessible without login"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))

        # Get some statistics for the landing page
        species_count = Species.query.count()
        program_count = ConservationProgram.query.count()
        return render_template('landing.html',
                           species_count=species_count,
                           program_count=program_count)
    except Exception as e:
        app.logger.error(f"Error in landing page: {str(e)}")
        return render_template('errors/500.html'), 500

@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route - requires login"""
    try:
        app.logger.info(f"User {current_user.username} accessing dashboard with role: {current_user.role}")

        if current_user.role == 'teacher':
            app.logger.info("Rendering teacher dashboard")
            return render_template('dashboard/teacher.html')
        elif current_user.role == 'student':
            app.logger.info("Rendering student dashboard")
            featured_species = Species.query.limit(5).all()
            return render_template('dashboard/student.html',
                                featured_species=featured_species)
        else:  # community member
            app.logger.info("Rendering community dashboard")
            active_programs = ConservationProgram.query.all()
            species_count = Species.query.count()
            # Get user contributions (sightings count)
            from models import SpeciesSighting
            user_contributions = SpeciesSighting.query.filter_by(user_id=current_user.id).count()
            return render_template('dashboard/community.html',
                                active_programs=active_programs,
                                species_count=species_count,
                                user_contributions=user_contributions)
    except Exception as e:
        app.logger.error(f"Error rendering dashboard: {str(e)}")
        db.session.rollback()
        return render_template('errors/500.html'), 500