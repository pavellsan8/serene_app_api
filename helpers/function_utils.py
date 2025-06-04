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
    
    @staticmethod
    def parse_youtube_duration(duration):
        hours_match = re.search(r'(\d+)H', duration)
        minutes_match = re.search(r'(\d+)M', duration)
        seconds_match = re.search(r'(\d+)S', duration)
        
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        seconds = int(seconds_match.group(1)) if seconds_match else 0
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"