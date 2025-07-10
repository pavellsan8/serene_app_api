from sqlalchemy.orm import aliased

from store.db import db

class QuestionnaireModel(db.Model):
    __tablename__ = 'Questionnaire'

    quest_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    feeling_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def get_user_feelings(cls, user_id):
        from models.m_feeling_model import MFeelingModel

        a = aliased(MFeelingModel)
        b = aliased(QuestionnaireModel)

        results = (
            db.session.query(a.feeling_id, a.description)
            .join(b, b.feeling_id == a.feeling_id)
            .filter(b.user_id == user_id)
            .all()
        )

        return [
            {
                "feeling_id": row.feeling_id, 
                "description": row.description,
            }
            for row in results
        ]