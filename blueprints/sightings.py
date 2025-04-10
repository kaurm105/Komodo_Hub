from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, app
from models import Species, SpeciesSighting
from forms import SightingForm
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import os

sightings = Blueprint('sightings', __name__)

UPLOAD_FOLDER = 'static/uploads/sightings'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Generate unique filename using timestamp
        base, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{base}_{timestamp}{ext}"

        # Ensure upload directory exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(filepath)
        return f'/static/uploads/sightings/{new_filename}'
    return None

@sightings.route('/sightings')
@login_required
def list_sightings():
    try:
        form = SightingForm()
        form.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name).all()]

        # Get sightings data
        sightings_query = SpeciesSighting.query.join(Species)

        if current_user.role == 'teacher':
            # Teachers can see all sightings
            sightings_list = sightings_query.order_by(SpeciesSighting.created_at.desc()).all()
        else:
            # Students and community members see only their own sightings
            sightings_list = sightings_query.filter_by(user_id=current_user.id).order_by(SpeciesSighting.created_at.desc()).all()

        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('sightings/partial_list.html', 
                                sightings=sightings_list,
                                form=form)

        # Regular request - return full template
        return render_template('sightings/list.html', 
                             sightings=sightings_list,
                             form=form)

    except Exception as e:
        app.logger.error(f'Error in sightings.list_sightings: {str(e)}')
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Error loading sightings content'}), 500
        flash('Error loading sightings. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))

@sightings.route('/sightings/map')
@login_required
def map_view():
    try:
        # Get all sightings with valid coordinates
        sightings_list = (SpeciesSighting.query
                         .join(Species)
                         .filter(
                             SpeciesSighting.latitude.isnot(None),
                             SpeciesSighting.longitude.isnot(None)
                         )
                         .order_by(SpeciesSighting.created_at.desc())
                         .all())

        app.logger.info(f'Retrieved {len(sightings_list)} sightings for map view')
        return render_template('sightings/map.html', sightings=sightings_list)
    except Exception as e:
        app.logger.error(f'Error in sightings.map_view: {str(e)}')
        flash('Error loading sightings map. Please try again.', 'error')
        return redirect(url_for('sightings.list_sightings'))

@sightings.route('/api/sightings/map')
@login_required
def get_sightings_map_data():
    try:
        sightings = (SpeciesSighting.query
                    .join(Species)
                    .filter(
                        SpeciesSighting.latitude.isnot(None),
                        SpeciesSighting.longitude.isnot(None)
                    )
                    .all())

        app.logger.info(f'Retrieved {len(sightings)} sightings for map data')

        return jsonify([{
            'id': s.id,
            'species': s.species.name,
            'lat': float(s.latitude),
            'lng': float(s.longitude),
            'description': s.description,
            'observer': s.user.username,  # Changed from observer to user
            'date': s.created_at.strftime('%Y-%m-%d'),
            'status': s.status,
            'image_url': s.image_url if s.image_url else None
        } for s in sightings])
    except Exception as e:
        app.logger.error(f'Error in sightings.get_sightings_map_data: {str(e)}')
        return jsonify({'error': 'Error loading map data'}), 500

@sightings.route('/sightings/report', methods=['POST'])
@login_required
def report_sighting():
    try:
        form = SightingForm()
        form.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name).all()]

        if form.validate_on_submit():
            # Handle image upload
            image_url = None
            if form.photos.data:
                image_url = save_uploaded_file(form.photos.data)

            sighting = SpeciesSighting(
                species_id=form.species_id.data,
                user_id=current_user.id,  # Changed from observer_id to user_id
                location=form.location.data,
                description=form.description.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                sighting_date=form.sighting_date.data,
                habitat_notes=form.habitat_notes.data,
                behavior_notes=form.behavior_notes.data,
                image_url=image_url,
                status='pending'  # Set initial status as pending
            )
            db.session.add(sighting)
            db.session.commit()

            app.logger.info(f'New sighting reported by {current_user.username} for species ID: {form.species_id.data}')
            flash('Sighting reported successfully! Waiting for verification.', 'success')
        else:
            app.logger.warning(f'Form validation failed: {form.errors}')
            flash('Please check your form inputs.', 'warning')

        return redirect(url_for('sightings.list_sightings'))
    except Exception as e:
        app.logger.error(f'Error in sightings.report_sighting: {str(e)}')
        db.session.rollback()
        flash('Error reporting sighting. Please try again.', 'error')
        return redirect(url_for('sightings.list_sightings'))