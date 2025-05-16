from datetime import datetime
from werkzeug.security import generate_password_hash

from store.db import db

class UsersModel(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(50), unique=True, nullable=False)
    user_password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    submit_questionnaire = db.Column(db.Boolean, default=False, nullable=False)
        
    @classmethod
    def hash_password(cls, password):
        return generate_password_hash(password)

    @classmethod
    def getEmailFirst(cls, email):
        return cls.query.filter(cls.user_email == email).first()
    
    def to_dict(self):
        return {
            "id": self.user_id,
            "name": self.user_name,
            "email": self.user_email,
            "created_at": self.created_at,
            "submit_questionnaire": self.submit_questionnaire,
        }

    @classmethod
    def updateUserPassword(cls, email, password):
        user = cls.query.filter_by(user_email=email).first()
        
        if user:
            user.user_password = cls.hash_password(password)
            db.session.add(user)
            db.session.commit()
            return True

        return False
    
    @classmethod
    def deleteUser(cls, email):
        user = cls.query.filter_by(user_email=email).first()
        
        if user:
            db.session.delete(user)
            db.session.commit()
            return True

        return False
