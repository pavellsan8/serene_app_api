from store.db import db

class VideoFavouriteModel(db.Model):
    __tablename__ = 'Video_Favourite'

    favvideo_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    video_id = db.Column(db.String(100), nullable=False)

    @classmethod
    def getAllVideoFavourites(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()
    
    @classmethod
    def getVideoFirstFavourite(cls, user_id, video_id):
        return cls.query.filter_by(user_id=user_id, video_id=video_id).first()