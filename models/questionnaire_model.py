from store.db import db

class QuestionnaireModel(db.Model):
    __tablename__ = 'Questionnaire'

    quest_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    feeling_id = db.Column(db.Integer, nullable=False)