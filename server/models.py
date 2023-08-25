from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
from datetime import datetime

class User(db.Model, SerializerMixin):

    __tablename__ = 'users'

    serialize_rules = ('-_password_hash',)

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable=False)
    _password_hash = db.Column(db.String)

    calendar = db.relationship('Calendar', back_populates='user', cascade='all, delete, delete-orphan')
    lists = db.relationship('List', back_populates='user', cascade='all, delete')

    @hybrid_property
    def password_hash(self):
        raise Exception('Password hashes may not be viewed')
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash =  bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )
        
    @validates('username')
    def validate_username(self, key, name):
        if not name or not isinstance(name, str):
            raise ValueError('Username must be non-empty string.')
        return name
    

class List(db.Model, SerializerMixin):

    __tablename__ = 'lists'
    
    serialize_rules = ('-user', '-tasks', '-event')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=True)
    
    tasks = db.relationship('Task', back_populates='list', cascade='all, delete, delete-orphan')
    user = db.relationship('User', back_populates='lists')
    event = db.relationship('Event', back_populates='lists')

    @validates('name')
    def validate_name(self, key, name):
        if not name or not isinstance(name, str):
            raise ValueError('List name must be non-empty string.')
        return name
    
class Calendar(db.Model, SerializerMixin):
    
    __tablename__ = 'calendars'

    serialize_rules = ('-user', '-events',)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    year = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='calendar')
    events = db.relationship('Event', back_populates='calendar', cascade='all, delete, delete-orphan')


class Event(db.Model, SerializerMixin):

    __tablename__ = 'events'

    serialize_rules = ('-calendar', '-lists')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)

    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.id', ondelete='CASCADE'))
    
    calendar = db.relationship('Calendar', back_populates='events')
    lists = db.relationship('List', back_populates='event')

    @validates('name')
    def validate_name(self, key, name):
        if not name or not isinstance(name, str):
            raise ValueError('List name must be non-empty string.')
        return name


class Task(db.Model, SerializerMixin):

    __tablename__ = 'tasks'

    serialize_rules = ('-list',)

    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String, nullable = False)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id', ondelete='CASCADE'))

    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False, default=0)

    list = db.relationship('List', back_populates='tasks')

    @validates('description')
    def validate_description(self, key, description):
        if not description or not isinstance(description, str):
            raise ValueError('Task description must be non-empty string!')
        return description
    
