from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import EducationalResource, UserProgress, ResourceTag
from forms import ResourceForm
from sqlalchemy import desc

education = Blueprint('education', __name__)

@education.route('/education')
@login_required
def resources():
    try:
        # Get filter parameters
        tag_filter = request.args.get('tag')
        search_query = request.args.get('search')
        resource_type = request.args.get('type')

        # Base query
        query = EducationalResource.query

        # Apply filters
        if tag_filter:
            query = query.join(EducationalResource.tags).filter(ResourceTag.name == tag_filter)
        if search_query:
            query = query.filter(EducationalResource.title.ilike(f'%{search_query}%'))
        if resource_type:
            query = query.filter(EducationalResource.resource_type == resource_type)

        # Get all available tags for the filter dropdown
        tags = ResourceTag.query.all()

        # Get resource types for the filter dropdown
        resource_types = db.session.query(EducationalResource.resource_type).distinct().all()
        resource_types = [r[0] for r in resource_types]

        # Execute query with sorting by latest first
        resources = query.order_by(desc(EducationalResource.created_at)).all()

        # Track progress for students
        if current_user.role == 'student':
            for resource in resources:
                progress = UserProgress.query.filter_by(
                    user_id=current_user.id,
                    content_type='resource',
                    content_id=resource.id
                ).first()

                if not progress:
                    progress = UserProgress(
                        user_id=current_user.id,
                        content_type='resource',
                        content_id=resource.id,
                        completed=False
                    )
                    db.session.add(progress)
            db.session.commit()

        return render_template('education/resources.html', 
                         resources=resources, 
                         tags=tags,
                         resource_types=resource_types,
                         current_tag=tag_filter,
                         current_type=resource_type,
                         search_query=search_query)
    except Exception as e:
        db.session.rollback()
        flash('Error loading educational resources. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))

@education.route('/education/add', methods=['GET', 'POST'])
@login_required
def add_resource():
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('education.resources'))

    form = ResourceForm()
    if form.validate_on_submit():
        try:
            resource = EducationalResource(
                title=form.title.data,
                content=form.content.data,
                resource_type=form.resource_type.data,
                author_id=current_user.id,
                is_public=True
            )
            db.session.add(resource)
            db.session.commit()
            flash('Resource added successfully!', 'success')
            return redirect(url_for('education.resources'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding resource. Please try again.', 'error')

    return render_template('education/add.html', form=form)