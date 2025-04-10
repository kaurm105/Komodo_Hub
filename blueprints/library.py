from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import LibraryResource
from forms import LibraryResourceForm

library = Blueprint('library', __name__)

@library.route('/library')
@library.route('/library/resources')
@login_required
def resources():
    # Get all public resources and resources authored by the user
    resources = LibraryResource.query.filter(
        (LibraryResource.is_public == True) |
        (LibraryResource.author_id == current_user.id)  # Show resources created by the current user
    ).order_by(LibraryResource.created_at.desc()).all()
    return render_template('library/list.html', resources=resources)

@library.route('/library/add', methods=['GET', 'POST'])
@login_required
def add_resource():
    if current_user.role not in ['teacher', 'community']:
        flash('Only teachers and community members can create library resources', 'error')
        return redirect(url_for('library.resources'))

    form = LibraryResourceForm()
    if form.validate_on_submit():
        resource = LibraryResource(
            title=form.title.data,
            content=form.content.data,
            resource_type=form.resource_type.data,
            is_public=form.is_public.data == 'True',
            author_id=current_user.id
        )

        db.session.add(resource)
        db.session.commit()
        flash('Resource created successfully!', 'success')
        return redirect(url_for('library.resources'))

    return render_template('library/create.html', form=form)

@library.route('/library/<int:id>')
@login_required
def view_resource(id):
    resource = LibraryResource.query.get_or_404(id)
    if not resource.is_public and resource.author_id != current_user.id:
        flash('You do not have permission to view this resource', 'error')
        return redirect(url_for('library.resources'))
    return render_template('library/view.html', resource=resource)