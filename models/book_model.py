from store.db import db

class BookModel(db.Model):
    __tablename__ = 'Book'

    book_id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    authors = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('M_Feeling.feeling_id'), nullable=False)

    # Relationship
    category = db.relationship('MFeelingModel', backref='books', lazy=True)
    favourites = db.relationship('BookFavouriteModel', backref='book', lazy=True)