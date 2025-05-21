from sqlalchemy import func
from sqlalchemy.orm import aliased

from store.db import db

class MusicModel(db.Model):
    __tablename__ = 'Music'

    music_id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    audio = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    album = db.Column(db.Integer, nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def getMusicByFeelingId(cls, user_id):
        from models.questionnaire_model import QuestionnaireModel

        a = aliased(QuestionnaireModel)
        b = aliased(MusicModel)

        data = db.session.query(
            b.music_id,
            b.title,
            b.audio,
            b.artist,
            b.album,
            b.thumbnail,
            b.duration,
        ).select_from(a).join(
            b,
            a.feeling_id == b.category_id,
        ).filter(
            a.user_id == user_id,
        ).order_by(
            func.random()
        ).all()

        return {
            'data': [
                {
                    'music_id': music.music_id,
                    'title': music.title,
                    'audio': music.audio,
                    'artist': music.artist,
                    'album': music.album,
                    'thumbnail': music.thumbnail,
                    'duration': music.duration
                } for music in data
            ]
        }