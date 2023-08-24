from models import User, db
from app import app
from datetime import datetime
    
with app.app_context():
    User.query.delete()
    db.session.commit()