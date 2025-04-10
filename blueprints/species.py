from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db, app
from models import Species, UserProgress, SpeciesSighting
from forms import SpeciesForm
from datetime import datetime
import logging

species = Blueprint('species', __name__)

@species.route('/species')
@login_required
def list():
    try:
        species_list = Species.query.all()
        app.logger.info(f'Successfully retrieved {len(species_list)} species')
        return render_template('species/list.html', 
                           species=species_list,
                           datetime=datetime)
    except Exception as e:
        app.logger.error(f'Error in species.list: {str(e)}')
        db.session.rollback()
        flash('Error loading species data. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))

@species.route('/species/<int:id>')
@login_required
def view(id):
    try:
        species_item = Species.query.get_or_404(id)
        app.logger.info(f'Viewing species {species_item.name} (ID: {id})')
        return render_template('species/view.html', 
                             species=species_item,
                             datetime=datetime)
    except Exception as e:
        app.logger.error(f'Error in species.view for ID {id}: {str(e)}')
        db.session.rollback()
        flash('Error loading species data. Please try again.', 'error')
        return redirect(url_for('species.list'))

@species.route('/my-sightings')
@login_required
def my_sightings():
    try:
        sightings = SpeciesSighting.query.filter_by(user_id=current_user.id)\
            .order_by(SpeciesSighting.created_at.desc()).all()
        app.logger.info(f'Retrieved {len(sightings)} sightings for user {current_user.id}')
        return render_template('species/my_sightings.html', sightings=sightings)
    except Exception as e:
        app.logger.error(f'Error in species.my_sightings: {str(e)}')
        db.session.rollback()
        flash('Error loading your sightings. Please try again.', 'error')
        return redirect(url_for('species.list'))

@species.route('/all-sightings')
@login_required
def all_sightings():
    if current_user.role not in ['teacher', 'community']:
        flash('Access denied. Only teachers and community members can view all sightings.', 'danger')
        return redirect(url_for('species.list'))

    # Get filter parameters
    role = request.args.get('role')
    date_range = request.args.get('date_range')
    sort = request.args.get('sort', 'date_desc')

    # Base query
    query = SpeciesSighting.query

    # Apply role filter
    if role:
        query = query.join(SpeciesSighting.observer).filter_by(role=role)

    # Apply date filter
    if date_range:
        if date_range == 'today':
            query = query.filter(SpeciesSighting.sighting_date >= datetime.today().date())
        elif date_range == 'week':
            query = query.filter(SpeciesSighting.sighting_date >= datetime.today() - timedelta(days=7))
        elif date_range == 'month':
            query = query.filter(SpeciesSighting.sighting_date >= datetime.today() - timedelta(days=30))

    # Apply sorting
    if sort == 'date_desc':
        query = query.order_by(desc(SpeciesSighting.sighting_date))
    elif sort == 'date_asc':
        query = query.order_by(asc(SpeciesSighting.sighting_date))
    elif sort == 'species':
        query = query.join(Species).order_by(Species.name)

    sightings = query.all()

    return render_template('species/all_sightings.html', 
                         sightings=sightings,
                         request=request)

@species.route('/species/add', methods=['GET', 'POST'])
@login_required
def add():
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('species.list'))

    form = SpeciesForm()
    if form.validate_on_submit():
        species = Species(
            name=form.name.data,
            scientific_name=form.scientific_name.data,
            description=form.description.data,
            population=form.population.data,
            conservation_status=form.conservation_status.data,
            habitat=form.habitat.data,
            threats=form.threats.data,
            created_by_id=current_user.id
        )
        db.session.add(species)
        db.session.commit()
        flash('Species added successfully!', 'success')
        return redirect(url_for('species.list'))
    return render_template('species/add.html', form=form)

@species.route('/species/<int:species_id>/report-sighting', methods=['POST'])
@login_required
def report_sighting(species_id):
    try:
        species = Species.query.get_or_404(species_id)
        location = request.form.get('location')
        sighting_date = request.form.get('sighting_date')
        description = request.form.get('description')

        if not location or not sighting_date:
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('species.view', id=species_id))

        sighting_date = datetime.strptime(sighting_date, '%Y-%m-%d')

        sighting = SpeciesSighting(
            species_id=species.id,
            user_id=current_user.id,
            location=location,
            sighting_date=sighting_date,
            description=description
        )

        db.session.add(sighting)
        db.session.commit()

        app.logger.info(f'New sighting reported for species {species.name} by user {current_user.id}')
        flash('Sighting reported successfully! It will be reviewed by our team.', 'success')

    except Exception as e:
        app.logger.error(f'Error in species.report_sighting for species {species_id}: {str(e)}')
        db.session.rollback()
        flash('Error reporting sighting. Please try again.', 'danger')

    return redirect(url_for('species.view', id=species_id))

@species.route('/sighting/<int:sighting_id>/update-status', methods=['POST'])
@login_required
def update_sighting_status(sighting_id):
    if current_user.role != 'teacher':
        flash('Only teachers can verify sightings.', 'danger')
        return redirect(url_for('species.all_sightings'))

    sighting = SpeciesSighting.query.get_or_404(sighting_id)
    new_status = request.form.get('status')

    if new_status in ['verified', 'rejected']:
        sighting.status = new_status
        db.session.commit()
        flash(f'Sighting status updated to {new_status}.', 'success')
    else:
        flash('Invalid status value.', 'danger')

    return redirect(url_for('species.all_sightings'))
from sqlalchemy import asc, desc