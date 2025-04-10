from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db, app
from models import ForumCategory, ForumThread, ForumPost, SpeciesSighting, Species, SightingComment, UserReputation, User, SpeciesIdentificationChallenge, UserIdentification, ForumUpvote # Added ForumUpvote
from forms import ThreadForm, PostForm, CategoryForm, SightingForm, CommentForm
from sqlalchemy import func, desc
import logging

forum = Blueprint('forum', __name__)

@forum.route('/forum')
@login_required
def index():
    try:
        # Get forum categories
        categories = ForumCategory.query.all()

        # Get recent threads
        recent_threads = ForumThread.query.order_by(ForumThread.created_at.desc()).limit(5).all()

        return render_template('forum/index.html',
                             categories=categories,
                             recent_threads=recent_threads)

    except Exception as e:
        app.logger.error(f'Error in forum.index: {str(e)}')
        flash('Error loading forum content. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))

@forum.route('/api/sightings/map')
@login_required
def get_sightings_map_data():
    sightings = SpeciesSighting.query.filter(
        SpeciesSighting.latitude.isnot(None),
        SpeciesSighting.longitude.isnot(None)
    ).all()

    return jsonify([{
        'id': s.id,
        'species': s.species.name,
        'lat': s.latitude,
        'lng': s.longitude,
        'description': s.description,
        'observer': s.observer.username,
        'date': s.sighting_date.strftime('%Y-%m-%d')
    } for s in sightings])

@forum.route('/challenge/<int:id>', methods=['GET', 'POST'])
@login_required
def species_challenge(id):
    challenge = SpeciesIdentificationChallenge.query.get_or_404(id)

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        is_correct = user_answer == challenge.correct_answer

        identification = UserIdentification(
            user_id=current_user.id,
            challenge_id=id,
            is_correct=is_correct,
            points_earned=challenge.points if is_correct else 0
        )
        db.session.add(identification)
        db.session.commit()

        if is_correct:
            flash(f'Correct! You earned {challenge.points} points!', 'success')
        else:
            flash('Not quite right. Try another challenge!', 'warning')

        return redirect(url_for('forum.index'))

    return render_template('forum/challenge.html', challenge=challenge)

@forum.route('/sightings/report', methods=['POST'])
@login_required
def report_sighting():
    form = SightingForm()
    form.species_id.choices = [(s.id, s.name) for s in Species.query.all()]

    if form.validate_on_submit():
        try:
            sighting = SpeciesSighting(
                species_id=form.species_id.data,
                user_id=current_user.id,
                location=form.location.data,
                description=form.description.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data
            )

            db.session.add(sighting)
            db.session.commit()

            # Update user reputation
            reputation = UserReputation.query.filter_by(user_id=current_user.id).first()
            if reputation:
                reputation.points += 10
                db.session.commit()

            flash('Sighting reported successfully! You earned 10 points!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error reporting sighting. Please try again.', 'error')
    else:
        flash('Please check your form inputs.', 'warning')

    return redirect(url_for('forum.index'))

@forum.route('/forum/sighting/<int:id>')
@login_required
def view_sighting(id):
    sighting = SpeciesSighting.query.get_or_404(id)
    comment_form = CommentForm()
    return render_template('forum/view_sighting.html', 
                         sighting=sighting,
                         comment_form=comment_form)

@forum.route('/forum/sighting/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    sighting = SpeciesSighting.query.get_or_404(id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = SightingComment(
            sighting_id=id,
            user_id=current_user.id,
            content=form.content.data
        )
        db.session.add(comment)
        sighting.comments_count += 1
        db.session.commit()

        # Update user reputation
        reputation = UserReputation.query.filter_by(user_id=current_user.id).first()
        if reputation:
            reputation.points += 5
            db.session.commit()

        flash('Comment added successfully!', 'success')
    return redirect(url_for('forum.view_sighting', id=id))


@forum.route('/forum/category/<int:id>')
@login_required
def view_category(id):
    category = ForumCategory.query.get_or_404(id)
    threads = ForumThread.query.filter_by(category_id=id)\
        .order_by(ForumThread.is_pinned.desc(), ForumThread.created_at.desc()).all()
    return render_template('forum/category.html', category=category, threads=threads)

@forum.route('/forum/thread/new/<int:category_id>', methods=['GET', 'POST'])
@login_required
def create_thread(category_id):
    category = ForumCategory.query.get_or_404(category_id)
    form = ThreadForm()

    if form.validate_on_submit():
        thread = ForumThread(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            category_id=category_id
        )
        db.session.add(thread)
        db.session.commit()
        flash('Thread created successfully!', 'success')
        return redirect(url_for('forum.view_thread', id=thread.id))

    return render_template('forum/create_thread.html', form=form, category=category)

@forum.route('/forum/thread/<int:id>')
@login_required
def view_thread(id):
    thread = ForumThread.query.get_or_404(id)
    # Increment view count
    thread.view_count += 1
    db.session.commit()

    posts = ForumPost.query.filter_by(thread_id=id)\
        .order_by(ForumPost.created_at).all()
    form = PostForm()
    return render_template('forum/view_thread.html', thread=thread, posts=posts, form=form)

@forum.route('/forum/thread/<int:id>/reply', methods=['POST'])
@login_required
def reply_thread(id):
    thread = ForumThread.query.get_or_404(id)
    if thread.is_locked and current_user.role != 'teacher':
        flash('This thread is locked.', 'warning')
        return redirect(url_for('forum.view_thread', id=id))

    form = PostForm()
    if form.validate_on_submit():
        post = ForumPost(
            content=form.content.data,
            author_id=current_user.id,
            thread_id=id
        )
        db.session.add(post)
        db.session.commit()
        flash('Reply posted successfully!', 'success')

    return redirect(url_for('forum.view_thread', id=id))

@forum.route('/forum/thread/<int:id>/toggle_pin', methods=['POST'])
@login_required
def toggle_pin_thread(id):
    if current_user.role != 'teacher':
        flash('Only teachers can pin/unpin threads.', 'danger')
        return redirect(url_for('forum.view_thread', id=id))

    thread = ForumThread.query.get_or_404(id)
    thread.is_pinned = not thread.is_pinned
    db.session.commit()
    flash(f'Thread {"pinned" if thread.is_pinned else "unpinned"} successfully!', 'success')
    return redirect(url_for('forum.view_thread', id=id))

@forum.route('/forum/thread/<int:id>/toggle_lock', methods=['POST'])
@login_required
def toggle_lock_thread(id):
    if current_user.role != 'teacher':
        flash('Only teachers can lock/unlock threads.', 'danger')
        return redirect(url_for('forum.view_thread', id=id))

    thread = ForumThread.query.get_or_404(id)
    thread.is_locked = not thread.is_locked
    db.session.commit()
    flash(f'Thread {"locked" if thread.is_locked else "unlocked"} successfully!', 'success')
    return redirect(url_for('forum.view_thread', id=id))

@forum.route('/forum/category/create', methods=['POST'])
@login_required
def create_category():
    if current_user.role != 'teacher':
        flash('Only teachers can create categories.', 'danger')
        return redirect(url_for('forum.index'))

    form = CategoryForm()
    if form.validate_on_submit():
        category = ForumCategory(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
    return redirect(url_for('forum.index'))

@forum.route('/forum/post/<int:id>/upvote', methods=['POST'])
@login_required
def upvote_post(id):
    try:
        post = ForumPost.query.get_or_404(id)

        # Check if user already upvoted this post
        existing_upvote = ForumUpvote.query.filter_by(
            user_id=current_user.id,
            post_id=id
        ).first()

        if existing_upvote:
            # Remove upvote if it exists
            db.session.delete(existing_upvote)
            post.upvotes_count -= 1
            message = 'Upvote removed'
            status = 'info'
        else:
            # Add new upvote
            upvote = ForumUpvote(user_id=current_user.id, post_id=id)
            db.session.add(upvote)
            post.upvotes_count += 1
            message = 'Post upvoted!'
            status = 'success'

        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'upvotes_count': post.upvotes_count,
                'message': message
            })

        flash(message, status)
        return redirect(url_for('forum.view_thread', id=post.thread_id))

    except Exception as e:
        app.logger.error(f'Error in forum.upvote_post: {str(e)}')
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Error processing upvote'}), 500
        flash('Error processing upvote. Please try again.', 'error')
        return redirect(url_for('forum.view_thread', id=post.thread_id))

@forum.route('/forum/post/<int:id>/reply', methods=['POST'])
@login_required
def reply_to_post(id):
    try:
        parent_post = ForumPost.query.get_or_404(id)
        form = PostForm()

        if form.validate_on_submit():
            reply = ForumPost(
                content=form.content.data,
                author_id=current_user.id,
                thread_id=parent_post.thread_id,
                parent_id=id
            )
            db.session.add(reply)
            db.session.commit()
            flash('Reply posted successfully!', 'success')
        else:
            flash('Please check your input.', 'warning')

        return redirect(url_for('forum.view_thread', id=parent_post.thread_id))

    except Exception as e:
        app.logger.error(f'Error in forum.reply_to_post: {str(e)}')
        db.session.rollback()
        flash('Error posting reply. Please try again.', 'error')
        return redirect(url_for('forum.view_thread', id=parent_post.thread_id))

@forum.route('/community-dashboard')
@login_required
def community_dashboard():
    try:
        app.logger.info('Loading community dashboard page')

        # Get recent sightings
        recent_sightings = (SpeciesSighting.query
                          .join(Species)
                          .join(User)
                          .order_by(SpeciesSighting.created_at.desc())
                          .limit(6)
                          .all())
        app.logger.info(f'Retrieved {len(recent_sightings)} recent sightings')

        # Get recent forum threads
        recent_threads = (ForumThread.query
                        .join(User, ForumThread.author_id == User.id)
                        .join(ForumCategory)
                        .order_by(ForumThread.created_at.desc())
                        .limit(5)
                        .all())
        app.logger.info(f'Retrieved {len(recent_threads)} recent threads')

        # Get community leaderboard
        leaderboard = (db.session.query(
            User,
            func.count(SpeciesSighting.id).label('sightings_count'),
            func.coalesce(func.sum(UserReputation.points), 0).label('points')
        )
        .outerjoin(SpeciesSighting, User.id == SpeciesSighting.user_id)
        .outerjoin(UserReputation, User.id == UserReputation.user_id)
        .group_by(User.id)
        .order_by(desc('sightings_count'), desc('points'))
        .limit(5)
        .all())
        app.logger.info(f'Retrieved {len(leaderboard)} leaderboard entries')

        # Initialize sighting form
        sighting_form = SightingForm()
        species_list = Species.query.order_by(Species.name).all()
        sighting_form.species_id.choices = [(s.id, s.name) for s in species_list]

        return render_template('forum/community_dashboard.html',
                            recent_sightings=recent_sightings,
                            recent_threads=recent_threads,
                            leaderboard=leaderboard,
                            sighting_form=sighting_form)

    except Exception as e:
        app.logger.error(f'Error in forum.community_dashboard: {str(e)}')
        db.session.rollback()
        return render_template('forum/community_dashboard.html',
                            recent_sightings=[],
                            recent_threads=[],
                            leaderboard=[],
                            sighting_form=SightingForm())