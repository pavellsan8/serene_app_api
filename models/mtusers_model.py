# Contoh Models
from store.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash

# Nama Model Disini
class MtUsersModel(db.Model):
    # Nama table di databaseb
    __tablename__ = 'mtusers'

    # Field tabel di database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.Text(), nullable=False)  
    registered_at = db.Column(db.DateTime, nullable=False)
    login_at = db.Column(db.DateTime, nullable=True)
    email = db.Column(db.String(50), nullable=False)
    ipadress_device = db.Column(db.String(255), nullable=False)

    # Query database disinitialized
    def hash_password(self, password):
        self.hashed_password = generate_password_hash(password)
        return self.hashed_password
    
    @classmethod
    def save_to_db(cls, instance):
        db.session.add(instance)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e 

    @classmethod
    def get_username_first(cls, username):
        return cls.query.filter(cls.username == username).first()
    
    @classmethod
    def update_login_time(cls, username, ipadress):
        user = cls.query.filter_by(username=username).first()
        dateLogin = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        if user:
            user.login_at = dateLogin
            user.ipadress_device = ipadress
            db.session.commit()

        return False