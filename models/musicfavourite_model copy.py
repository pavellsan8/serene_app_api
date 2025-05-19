from store.db import db

class MusicFavouriteModel(db.Model):
    __tablename__ = 'Music_Favourite'

    favmusic_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    music_id = db.Column(db.String(100), db.ForeignKey('Music.music_id'), nullable=False)