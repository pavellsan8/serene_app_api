from store.db import db

class VideoFavouriteModel(db.Model):
    __tablename__ = 'Video_Favourite'

    favvideo_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    video_id = db.Column(db.String(100), db.ForeignKey('Video.video_id'), nullable=False)