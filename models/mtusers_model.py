from datetime import datetime

from store.db import db
from werkzeug.security import generate_password_hash

class MtUsersModel(db.Model):
    __tablename__ = 'mtusers'

    userId = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(100), nullable=False)
    userEmail = db.Column(db.String(50), unique=True, nullable=False)
    userPassword = db.Column(db.Text(), nullable=False)  
    userCreatedAt = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc), nullable=False)
    userLoginAt = db.Column(db.DateTime, nullable=True)
    
    @classmethod
    def saveToDb(cls, instance):
        db.session.add(instance)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e 

    @classmethod
    def getEmailFirst(cls, email):
        return cls.query.with_entities(cls.userId, cls.userEmail, cls.userPassword).filter(cls.userEmail == email).first()
    
    @classmethod
    def updateLoginTime(cls, userId, userEmail):
        user = cls.query.filter_by(userId=userId, userEmail=userEmail).first()
        dateLogin = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        if user:
            user.login_at = dateLogin
            db.session.commit()

        return False