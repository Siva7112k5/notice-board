from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for students and admins"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=True) 
    phone = db.Column(db.String(15))
    batch = db.Column(db.String(10))
    profile_pic = db.Column(db.String(200), default='default.jpg')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    notices_created = db.relationship('Notice', backref='author', lazy=True, foreign_keys='Notice.created_by')
    saved_notices = db.relationship('SavedNotice', backref='user', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def unread_notifications_count(self):
        """Get count of unread notifications"""
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()
    
    @property
    def unread_notifications(self):
        """Get unread notifications"""
        return Notification.query.filter_by(user_id=self.id, is_read=False).order_by(Notification.created_at.desc()).all()
    
    def __repr__(self):
        return f'<User {self.username}>'


class Notice(db.Model):
    """Notice model for announcements"""
    __tablename__ = 'notice'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='normal')
    banner_image = db.Column(db.String(200))
    attachment = db.Column(db.String(200))
    views = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    saved_by = db.relationship('SavedNotice', backref='notice', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='notice', lazy=True, cascade='all, delete-orphan')
    
    @property
    def is_active(self):
        """Check if notice is still active"""
        if self.expiry_date:
            return datetime.utcnow() <= self.expiry_date
        return True
    
    @property
    def time_remaining(self):
        """Get time remaining until expiry"""
        if self.expiry_date:
            remaining = self.expiry_date - datetime.utcnow()
            days = remaining.days
            hours = remaining.seconds // 3600
            if days > 0:
                return f"{days} days"
            elif hours > 0:
                return f"{hours} hours"
            else:
                return "Expiring soon"
        return "No expiry"
    
    def __repr__(self):
        return f'<Notice {self.title}>'


class SavedNotice(db.Model):
    """Model for saved notices"""
    __tablename__ = 'saved_notice'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notice_id = db.Column(db.Integer, db.ForeignKey('notice.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'notice_id', name='unique_user_notice'),)
    
    def __repr__(self):
        return f'<SavedNotice user={self.user_id} notice={self.notice_id}>'


class Comment(db.Model):
    """Model for comments on notices"""
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notice_id = db.Column(db.Integer, db.ForeignKey('notice.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comment {self.id}>'


class Notification(db.Model):
    """Model for user notifications"""
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, success, warning, danger
    link = db.Column(db.String(200))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        db.session.commit()
    
    def __repr__(self):
        return f'<Notification {self.title}>'


class ContactMessage(db.Model):
    """Model for contact form messages"""
    __tablename__ = 'contact_message'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        db.session.commit()
    
    def reply_to_message(self, reply_text):
        """Add reply to message"""
        self.reply = reply_text
        self.replied_at = datetime.utcnow()
        self.is_read = True
        db.session.commit()
    
    def __repr__(self):
        return f'<ContactMessage {self.subject}>'
    
class User(db.Model, UserMixin):
    # ... existing code ...
    
    @property
    def unread_notifications_count(self):
        """Get count of unread notifications"""
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()
    
    @property
    def unread_notifications(self):
        """Get unread notifications"""
        return Notification.query.filter_by(user_id=self.id, is_read=False).order_by(Notification.created_at.desc()).all()    