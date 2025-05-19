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