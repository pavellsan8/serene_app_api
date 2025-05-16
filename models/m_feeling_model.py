from store.db import db

class MFeelingModel(db.Model):
    __tablename__ = 'M_Feeling'

    feeling_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'feeling_id': self.feeling_id,
            'description': self.description
        }

    @classmethod
    def get_all_feelings(cls):
        feelings = cls.query.all()  # Fetch all rows
        feeling_list = [feeling.to_dict() for feeling in feelings]  # Convert each row to a dictionary
        return feeling_list