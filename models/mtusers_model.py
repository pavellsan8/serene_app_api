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
    def hash_password(self, password):
        self.hashed_password = generate_password_hash(password)
        return self.hashed_password

    @classmethod
    def getEmailFirst(cls, email):
        return cls.query.filter(cls.userEmail == email).first()
    
    @classmethod
    def updateLoginTime(cls, email):
        user = cls.query.filter_by(userEmail=email).first()
        dateLogin = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        if user:
            user.userLoginAt = dateLogin
            db.session.commit()

        return False

    @classmethod
    def updateUserPassword(cls, email, password):
        user = cls.query.filter_by(userEmail=email).first()
        
        if user:
            user.userPassword = password
            db.session.commit()

        return False