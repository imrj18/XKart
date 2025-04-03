from models.db import db
from flask_login import UserMixin
from datetime import datetime


# Admin Model
class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    role = db.Column(db.Enum('superadmin', 'admin', name='role_types'), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Link to the Log model
    logs = db.relationship('Log', backref='admin', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Admin {self.username} | Role: {self.role}>'

    @classmethod
    def get_by_email(cls, email):
        """Retrieve an Admin by email."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def create_admin(cls, username, email, password, role='admin'):
        """Create and save a new admin."""
        hashed_password = cls.hash_password(password)
        new_admin = cls(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_admin)
        db.session.commit()
        return new_admin

    @staticmethod
    def hash_password(password):
        """Hash a plaintext password."""
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @property
    def is_admin(self):
        """Check if the user is an admin."""
        return True


# Log Model
class Log(db.Model):
    __tablename__ = 'logs'
    log_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Log {self.action} by Admin ID {self.admin_id}>'

    @classmethod
    def create_log(cls, admin_id, action):
        """Create and save a new log."""
        new_log = cls(admin_id=admin_id, action=action)
        db.session.add(new_log)
        db.session.commit()
        return new_log
