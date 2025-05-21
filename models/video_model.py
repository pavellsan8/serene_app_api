# from sqlalchemy import func
from sqlalchemy.orm import aliased

from store.db import db

class VideoModel(db.Model):
    __tablename__ = 'Video'

    video_id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    yt_link = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(1000), nullable=False)
    published_at = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def getVideoByFeelingId(cls, user_id):
        from models.questionnaire_model import QuestionnaireModel

        a = aliased(QuestionnaireModel)
        b = aliased(VideoModel)

        data = db.session.query(
            b.video_id,
            b.title,
            b.yt_link,
            b.channel,
            b.published_at,
            b.description,
            b.thumbnail,
            b.duration,
        ).select_from(a).join(
            b,
            a.feeling_id == b.category_id,
        ).filter(
            a.user_id == user_id,
        ).order_by(
            # func.random()
            b.video_id
        ).all()

        return {
            'data': [
                {
                    'video_id': video.video_id,
                    'title': video.title,
                    'yt_link': video.yt_link,
                    'channel': video.channel,
                    'published_at': video.published_at,
                    'description': video.description,
                    'thumbnail': video.thumbnail,
                    'duration': video.duration
                } for video in data
            ]
        }