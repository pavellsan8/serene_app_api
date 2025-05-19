from store.db import db

class BookModel(db.Model):
    __tablename__ = 'Book'

    book_id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, nullable=False)