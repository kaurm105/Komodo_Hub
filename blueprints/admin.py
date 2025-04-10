from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User, Species, LibraryResource, ForumThread, ForumPost, ForumCategory
from models import SpeciesSighting, ConservationProgram, Achievement
import logging
from functools import wraps

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

# Decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            logger.warning(f"Unauthorized access attempt to admin area by user: {current_user.username if current_user.is_authenticated else 'anonymous'}")
            flash('You do not have permission to access this area.', 'danger')
            return redirect(url_for('main.landing'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard showing system overview"""
    stats = {
        'users': User.query.count(),
        'species': Species.query.count(),
        'resources': LibraryResource.query.count(),
        'sightings': SpeciesSighting.query.count(),
        'forum_threads': ForumThread.query.count(),
        'forum_posts': ForumPost.query.count()
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_species = Species.query.order_by(Species.created_at.desc()).limit(10).all()
    recent_posts = ForumPost.query.order_by(ForumPost.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, 
                          recent_users=recent_users, 
                          recent_species=recent_species,
                          recent_posts=recent_posts,
                          title="Admin Dashboard")

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """View and manage all users"""
    users = User.query.all()
    return render_template('admin/users.html', users=users, title="Manage Users")

@admin_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit a specific user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        is_admin = 'is_admin' in request.form
        
        user.username = username
        user.email = email
        user.role = role
        user.is_admin = is_admin
        
        # Update password only if provided
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
            
        db.session.commit()
        flash(f'User {username} updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user, title=f"Edit User - {user.username}")

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/database')
@login_required
@admin_required
def database_management():
    """Database management interface"""
    models = [
        {'name': 'Users', 'count': User.query.count(), 'url': url_for('admin.manage_users')},
        {'name': 'Species', 'count': Species.query.count(), 'url': url_for('admin.manage_species')},
        {'name': 'Library Resources', 'count': LibraryResource.query.count(), 'url': url_for('admin.manage_resources')},
        {'name': 'Species Sightings', 'count': SpeciesSighting.query.count(), 'url': url_for('admin.manage_sightings')},
        {'name': 'Forum Categories', 'count': ForumCategory.query.count(), 'url': url_for('admin.manage_forum_categories')},
        {'name': 'Forum Threads', 'count': ForumThread.query.count(), 'url': url_for('admin.manage_forum_threads')},
        {'name': 'Forum Posts', 'count': ForumPost.query.count(), 'url': url_for('admin.manage_forum_posts')},
        {'name': 'Conservation Programs', 'count': ConservationProgram.query.count(), 'url': url_for('admin.manage_programs')}
    ]
    
    return render_template('admin/database.html', models=models, title="Database Management")

@admin_bp.route('/species')
@login_required
@admin_required
def manage_species():
    """View and manage all species"""
    species = Species.query.all()
    return render_template('admin/species.html', species=species, title="Manage Species")

@admin_bp.route('/resources')
@login_required
@admin_required
def manage_resources():
    """View and manage all library resources"""
    resources = LibraryResource.query.all()
    return render_template('admin/resources.html', resources=resources, title="Manage Resources")

@admin_bp.route('/forum/categories')
@login_required
@admin_required
def manage_forum_categories():
    """View and manage forum categories"""
    categories = ForumCategory.query.all()
    return render_template('admin/forum_categories.html', categories=categories, title="Manage Forum Categories")

@admin_bp.route('/forum/threads')
@login_required
@admin_required
def manage_forum_threads():
    """View and manage forum threads"""
    threads = ForumThread.query.all()
    return render_template('admin/forum_threads.html', threads=threads, title="Manage Forum Threads")

@admin_bp.route('/forum/posts')
@login_required
@admin_required
def manage_forum_posts():
    """View and manage forum posts"""
    posts = ForumPost.query.all()
    return render_template('admin/forum_posts.html', posts=posts, title="Manage Forum Posts")

@admin_bp.route('/sightings')
@login_required
@admin_required
def manage_sightings():
    """View and manage species sightings"""
    sightings = SpeciesSighting.query.all()
    return render_template('admin/sightings.html', sightings=sightings, title="Manage Sightings")

@admin_bp.route('/programs')
@login_required
@admin_required
def manage_programs():
    """View and manage conservation programs"""
    programs = ConservationProgram.query.all()
    return render_template('admin/programs.html', programs=programs, title="Manage Programs")

@admin_bp.route('/achievements')
@login_required
@admin_required
def manage_achievements():
    """View and manage user achievements"""
    achievements = Achievement.query.all()
    return render_template('admin/achievements.html', achievements=achievements, title="Manage Achievements")

# API endpoints for admin actions
@admin_bp.route('/api/users/change-role', methods=['POST'])
@login_required
@admin_required
def api_change_user_role():
    """API endpoint to change a user's role"""
    data = request.json
    user_id = data.get('user_id')
    new_role = data.get('role')
    
    if not user_id or not new_role:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    user.role = new_role
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'Role updated to {new_role}',
        'user_id': user_id,
        'new_role': new_role
    })

@admin_bp.route('/api/users/toggle-admin', methods=['POST'])
@login_required
@admin_required
def api_toggle_admin():
    """API endpoint to toggle admin status"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Missing user_id parameter'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Prevent removing admin status from yourself
    if user.id == current_user.id and user.is_admin:
        return jsonify({'success': False, 'message': 'Cannot remove your own admin status'}), 403
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'Admin status toggled to {user.is_admin}',
        'user_id': user_id,
        'is_admin': user.is_admin
    })