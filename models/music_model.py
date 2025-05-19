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
    category_id = db.Column(db.Integer, db.ForeignKey('M_Feeling.feeling_id'), nullable=False)

    # Relationship
    category = db.relationship('MFeelingModel', backref='musics', lazy=True)
    favourites = db.relationship('MusicFavouriteModel', backref='music', lazy=True)