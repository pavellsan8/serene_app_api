from sqlalchemy import func
from sqlalchemy.orm import aliased

from store.db import db

class MusicFavouriteModel(db.Model):
    __tablename__ = 'Music_Favourite'

    favmusic_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    music_id = db.Column(db.String(100), nullable=False)
    saved_at = db.Column(db.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    @classmethod
    def getAllMusicFavourites(cls, user_id):
        from models.music_model import MusicModel

        a = aliased(MusicFavouriteModel)
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
            a.music_id == b.music_id
        ).filter(
            a.user_id == user_id
        ).order_by(
            a.saved_at.desc()
        )

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
    
    @classmethod
    def getMusicFirstFavourite(cls, user_id, music_id):
        return cls.query.filter_by(user_id=user_id, music_id=music_id).first()