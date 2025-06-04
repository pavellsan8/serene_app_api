import re

from store.db import db

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

class FeatureUtils:
    @staticmethod
    def extract_year(date):
        if date == 'Unknown':
            return date
        
        match = re.match(r'\d{4}', date)
        return int(match.group(0)) if match else None
    
    @staticmethod
    def format_duration(seconds):
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        
        return f"{minutes:02}:{remaining_seconds:02}"