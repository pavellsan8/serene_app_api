from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DbUtils:
    @staticmethod
    def save_to_db(instance):
        db.session.add(instance)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e 
        
    @staticmethod
    def delete_from_db(instance):
        db.session.delete(instance)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        

    @staticmethod
    def update_in_db(instance):
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e