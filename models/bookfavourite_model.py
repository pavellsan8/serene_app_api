from store.db import db

class BookFavouriteModel(db.Model):
    __tablename__ = 'Book_Favourite'

    favbook_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    book_id = db.Column(db.String(100), db.ForeignKey('Book.book_id'), nullable=False)