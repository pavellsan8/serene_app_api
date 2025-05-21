from sqlalchemy import func
from sqlalchemy.orm import aliased

from store.db import db

class VideoFavouriteModel(db.Model):
    __tablename__ = 'Video_Favourite'

    favvideo_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    video_id = db.Column(db.String(100), nullable=False)
    saved_at = db.Column(db.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    @classmethod
    def getAllVideoFavourites(cls, user_id):
        from models.video_model import VideoModel

        a = aliased(VideoFavouriteModel)
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
            a.video_id == b.video_id
        ).filter(
            a.user_id == user_id
        ).order_by(
            a.saved_at.desc()
        )

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
    
    @classmethod
    def getVideoFirstFavourite(cls, user_id, video_id):
        return cls.query.filter_by(user_id=user_id, video_id=video_id).first()