from models import User, Calendar,db
from app import app
from datetime import datetime
    
with app.app_context():
    User.query.delete()
    Calendar.query.delete()
    
    # mark = User(
    #     username = 'Mark',
    # )
    # mark.password_hash = 'idgaf123'
    # db.session.add(mark)
    # db.session.commit()
    # date_time = datetime.now()

    # calendar = Calendar(
    #     user_id = mark.id,
    #     year = date_time.year
    # )

    # db.session.add(calendar)
    db.session.commit()
