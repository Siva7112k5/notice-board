import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Notice, SavedNotice, Comment, Notification, ContactMessage
from forms import (
    LoginForm, RegistrationForm, NoticeForm, 
    ContactForm, ProfileUpdateForm
)

# ... rest of your app.py code
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Ensure upload directory exists
os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'uploads', 'banners'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'uploads', 'profiles'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'uploads', 'attachments'), exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor to inject current year and categories
@app.context_processor
def inject_globals():
    categories = ['Important', 'Event', 'Academic', 'Holiday', 'Exam', 'Result', 'General']
    return {
        'current_year': datetime.utcnow().year,
        'categories': categories,
        'now': datetime.utcnow()
    }

# Home Page
@app.route('/')
@app.route('/home')
def index():
    page = request.args.get('page', 1, type=int)
    
    # Get featured notices
    featured_notices = Notice.query.filter_by(
        is_published=True, is_featured=True
    ).filter(
        (Notice.expiry_date.is_(None)) | (Notice.expiry_date > datetime.utcnow())
    ).order_by(Notice.created_at.desc()).limit(5).all()
    
    # Get recent notices
    recent_notices = Notice.query.filter_by(is_published=True).filter(
        (Notice.expiry_date.is_(None)) | (Notice.expiry_date > datetime.utcnow())
    ).order_by(Notice.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    
    # Get notices by category
    important_notices = Notice.query.filter_by(
        category='Important', is_published=True
    ).filter(
        (Notice.expiry_date.is_(None)) | (Notice.expiry_date > datetime.utcnow())
    ).order_by(Notice.created_at.desc()).limit(4).all()
    
    event_notices = Notice.query.filter_by(
        category='Event', is_published=True
    ).filter(
        (Notice.expiry_date.is_(None)) | (Notice.expiry_date > datetime.utcnow())
    ).order_by(Notice.created_at.desc()).limit(4).all()
    
    academic_notices = Notice.query.filter_by(
        category='Academic', is_published=True
    ).filter(
        (Notice.expiry_date.is_(None)) | (Notice.expiry_date > datetime.utcnow())
    ).order_by(Notice.created_at.desc()).limit(4).all()
    
    return render_template('index.html',
                         featured_notices=featured_notices,
                         recent_notices=recent_notices,
                         important_notices=important_notices,
                         event_notices=event_notices,
                         academic_notices=academic_notices)

@app.route('/notices')
def all_notices():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all')
    
    # Base query - get ALL published notices
    query = Notice.query.filter_by(is_published=True)
    
    # Optional: Remove expiry date filter temporarily to see all notices
    # query = Notice.query.filter_by(is_published=True).filter(
    #     (Notice.expiry_date.is_(None)) | (Notice.expiry_date > datetime.utcnow())
    # )
    
    # Apply category filter if specified
    if category != 'all':
        query = query.filter_by(category=category)
    
    # Order by priority and date
    notices = query.order_by(
        Notice.priority.desc(),
        Notice.created_at.desc()
    ).paginate(page=page, per_page=9, error_out=False)
    
    # Get all categories for filter
    categories = db.session.query(Notice.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('all_notices.html', 
                         notices=notices, 
                         current_category=category,
                         categories=categories)

# Notice Detail Page
@app.route('/notice/<int:id>')
def notice_detail(id):
    notice = Notice.query.get_or_404(id)
    
    # Increment view count
    notice.views += 1
    db.session.commit()
    
    # Check if user saved this notice
    is_saved = False
    if current_user.is_authenticated:
        is_saved = SavedNotice.query.filter_by(
            user_id=current_user.id, notice_id=notice.id
        ).first() is not None
    
    # Get related notices
    related_notices = Notice.query.filter_by(
        category=notice.category, is_published=True
    ).filter(Notice.id != notice.id).filter(
        (Notice.expiry_date.is_(None)) | (Notice.expiry_date > datetime.utcnow())
    ).limit(3).all()
    
    return render_template('notice_detail.html',
                         notice=notice,
                         is_saved=is_saved,
                         related_notices=related_notices)

# About Page
@app.route('/about')
def about():
    # Get admin details
    admin = User.query.filter_by(is_admin=True).first()
    return render_template('about.html', admin=admin)

# Contact Page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', form=form)

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_active:
                login_user(user, remember=form.remember.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                if user.is_admin:
                    return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Your account is deactivated. Contact admin.', 'danger')
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            roll_number=form.roll_number.data,
            department=form.department.data,
            semester=form.semester.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        # Update basic info
        if form.full_name.data:
            current_user.full_name = form.full_name.data
        
        if form.phone.data:
            current_user.phone = form.phone.data
        
        # Handle profile picture
        if form.profile_pic.data:
            filename = secure_filename(form.profile_pic.data.filename)
            # Add timestamp to filename to avoid duplicates
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{datetime.utcnow().timestamp()}{ext}"
            filepath = os.path.join(app.static_folder, 'uploads', 'profiles', filename)
            form.profile_pic.data.save(filepath)
            current_user.profile_pic = filename
        
        # Handle password change
        if form.new_password.data and form.current_password.data:
            if current_user.check_password(form.current_password.data):
                current_user.set_password(form.new_password.data)
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('profile'))
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        # Pre-populate form with current user data
        form.full_name.data = current_user.full_name
        form.phone.data = current_user.phone
    
    # Get user's saved notices
    saved_notices = SavedNotice.query.filter_by(user_id=current_user.id)\
        .order_by(SavedNotice.saved_at.desc()).all()
    
    return render_template('profile.html', form=form, saved_notices=saved_notices)

# Save/Unsave Notice
@app.route('/notice/<int:id>/save')
@login_required
def save_notice(id):
    notice = Notice.query.get_or_404(id)
    
    saved = SavedNotice.query.filter_by(
        user_id=current_user.id, notice_id=notice.id
    ).first()
    
    if saved:
        db.session.delete(saved)
        flash('Notice removed from saved', 'info')
    else:
        saved = SavedNotice(user_id=current_user.id, notice_id=notice.id)
        db.session.add(saved)
        flash('Notice saved successfully!', 'success')
    
    db.session.commit()
    return redirect(request.referrer or url_for('notice_detail', id=id))

# Share Notice
@app.route('/notice/<int:id>/share')
def share_notice(id):
    notice = Notice.query.get_or_404(id)
    # Generate shareable link or QR code
    share_url = url_for('notice_detail', id=id, _external=True)
    return jsonify({'url': share_url})

# ============= ADMIN ROUTES =============
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
    total_notices = Notice.query.count()
    total_students = User.query.filter_by(is_admin=False).count()
    active_notices = Notice.query.filter(
        (Notice.expiry_date.is_(None)) | (Notice.expiry_date > datetime.utcnow())
    ).count()
    total_messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    
    recent_notices = Notice.query.order_by(Notice.created_at.desc()).limit(5).all()
    recent_students = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/admin_dashboard.html',
                         total_notices=total_notices,
                         total_students=total_students,
                         active_notices=active_notices,
                         total_messages=total_messages,
                         unread_messages=unread_messages,
                         recent_notices=recent_notices,
                         recent_students=recent_students)

@app.route('/admin/notices')
@login_required
def manage_notices():
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    notices = Notice.query.order_by(Notice.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/manage_notices.html', notices=notices)

@app.route('/admin/notice/add', methods=['GET', 'POST'])
@login_required
def add_notice():
    if not current_user.is_admin:
        abort(403)
    
    form = NoticeForm()
    if form.validate_on_submit():
        notice = Notice(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            priority=form.priority.data,
            is_featured=form.is_featured.data,
            start_date=form.start_date.data,  # Make sure this matches your form
            expiry_date=form.expiry_date.data,  # Make sure this matches your form
            created_by=current_user.id
        )
        # ... rest of the code
        
        # Handle banner image
        if form.banner_image.data:
            filename = secure_filename(form.banner_image.data.filename)
            filepath = os.path.join(app.static_folder, 'uploads', 'banners', filename)
            form.banner_image.data.save(filepath)
            notice.banner_image = filename
        
        # Handle attachment
        if form.attachment.data:
            filename = secure_filename(form.attachment.data.filename)
            filepath = os.path.join(app.static_folder, 'uploads', 'attachments', filename)
            form.attachment.data.save(filepath)
            notice.attachment = filename
        
        db.session.add(notice)
        db.session.commit()
        
        # Create notifications for all students
        students = User.query.filter_by(is_admin=False).all()
        for student in students:
            notification = Notification(
                user_id=student.id,
                title='New Notice Posted',
                message=f'New notice: {notice.title}',
                type='info',
                link=url_for('notice_detail', id=notice.id)
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('Notice added successfully!', 'success')
        return redirect(url_for('manage_notices'))
    
    return render_template('admin/add_notice.html', form=form)

@app.route('/admin/notice/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_notice(id):
    if not current_user.is_admin:
        abort(403)
    
    notice = Notice.query.get_or_404(id)
    form = NoticeForm(obj=notice)
    
    if form.validate_on_submit():
        notice.title = form.title.data
        notice.content = form.content.data
        notice.category = form.category.data
        notice.priority = form.priority.data
        notice.is_featured = form.is_featured.data
        notice.start_date = form.start_date.data
        notice.expiry_date = form.expiry_date.data
        
        # Handle banner image
        if form.banner_image.data:
            filename = secure_filename(form.banner_image.data.filename)
            filepath = os.path.join(app.static_folder, 'uploads', 'banners', filename)
            form.banner_image.data.save(filepath)
            notice.banner_image = filename
        
        # Handle attachment
        if form.attachment.data:
            filename = secure_filename(form.attachment.data.filename)
            filepath = os.path.join(app.static_folder, 'uploads', 'attachments', filename)
            form.attachment.data.save(filepath)
            notice.attachment = filename
        
        notice.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Notice updated successfully!', 'success')
        return redirect(url_for('manage_notices'))
    
    return render_template('admin/edit_notice.html', form=form, notice=notice)

@app.route('/admin/notice/delete/<int:id>')
@login_required
def delete_notice(id):
    if not current_user.is_admin:
        abort(403)
    
    notice = Notice.query.get_or_404(id)
    db.session.delete(notice)
    db.session.commit()
    flash('Notice deleted successfully!', 'success')
    return redirect(url_for('manage_notices'))

@app.route('/admin/students')
@login_required
def manage_students():
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    students = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/manage_students.html', students=students)



@app.route('/admin/student/toggle/<int:id>')
@login_required
def toggle_student(id):
    if not current_user.is_admin:
        abort(403)
    
    student = User.query.get_or_404(id)
    if not student.is_admin:
        student.is_active = not student.is_active
        db.session.commit()
        status = 'activated' if student.is_active else 'deactivated'
        flash(f'Student {status} successfully!', 'success')
    
    return redirect(url_for('manage_students'))

@app.route('/admin/messages')
@login_required
def manage_messages():
    if not current_user.is_admin:
        abort(403)
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/message/<int:id>')
@login_required
def view_message(id):
    if not current_user.is_admin:
        abort(403)
    
    message = ContactMessage.query.get_or_404(id)
    message.is_read = True
    db.session.commit()
    return render_template('admin/message_detail.html', message=message)



@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        # Update banner settings
        banner_title = request.form.get('banner_title')
        banner_subtitle = request.form.get('banner_subtitle')
        
        # Save to config or database
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Create initial admin user
@app.cli.command("create-admin")
def create_admin():
    """Create admin user"""
    admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            username='admin',
            email=Config.ADMIN_EMAIL,
            full_name='System Administrator',
            roll_number='ADMIN001',
            department='Administration',
            semester=1,  # Add a default semester value for admin
            is_admin=True
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully!')
    else:
        print('Admin user already exists.')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)