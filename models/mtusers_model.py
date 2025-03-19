from datetime import datetime
from werkzeug.security import generate_password_hash

from store.db import db
from helpers.function_utils import *

class MtUsersModel(db.Model):
    __tablename__ = 'mtusers'

    userId = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(100), nullable=False)
    userEmail = db.Column(db.String(50), unique=True, nullable=False)
    userPassword = db.Column(db.Text(), nullable=False)  
    userPhoneNumber = db.Column(db.Text(), nullable=True)
    userCreatedAt = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc), nullable=False)
    userLoginAt = db.Column(db.DateTime, nullable=True)
    userUpdatedAt = db.Column(db.DateTime, nullable=True)
    userQuestionnaireStatus = db.Column(db.String(1), server_default='F', nullable=False)
        
    @classmethod
    def hash_password(cls, password):
        hashed_password = generate_password_hash(password)
        return hashed_password.replace("scrypt:32768:8:1$", "", 1)

    @classmethod
    def getEmailFirst(cls, email):
        return cls.query.filter(cls.userEmail == email).first()
    
    def to_dict(self):
        return {
            "userId": self.userId,
            "userName": self.userName,
            "userEmail": self.userEmail,
        }
    
    @classmethod
    def updateUserProfile(cls, name, email, phnum):
        user = cls.query.filter_by(userEmail=email).first()

        if user:
            user.userName = name
            user.userEmail = email
            user.userPhoneNumber = phnum
            user.userUpdatedAt = datetime.now(datetime.timezone.utc)
            DbUtils.update_in_db(user)
            return True

        return False
    
    @classmethod
    def updateLoginTime(cls, email):
        user = cls.query.filter_by(userEmail=email).first()
        
        if user:
            user.userLoginAt = datetime.now(datetime.timezone.utc)
            DbUtils.update_in_db(user)
            return True

        return False

    @classmethod
    def updateUserPassword(cls, email, password):
        user = cls.query.filter_by(userEmail=email).first()
        
        if user:
            user.userPassword = password
            DbUtils.update_in_db(user)
            return True

        return False
    
    @classmethod
    def deleteUser(cls, email):
        user = cls.query.filter_by(userEmail=email).first()
        
        if user:
            DbUtils.delete_from_db(user)
            return True

        return False