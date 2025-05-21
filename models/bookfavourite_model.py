from sqlalchemy import func
from sqlalchemy.orm import aliased

from store.db import db

class BookFavouriteModel(db.Model):
    __tablename__ = 'Book_Favourite'

    favbook_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.String(100), nullable=False)
    saved_at = db.Column(db.TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    @classmethod
    def getAllBookFavourites(cls, user_id):
        from models.book_model import BookModel

        a = aliased(BookFavouriteModel)
        b = aliased(BookModel)

        data = db.session.query(
            b.book_id,
            b.title,
            b.authors,
            b.description,
            b.pages,
            b.date,
            b.thumbnail,
            b.url,
        ).select_from(a).join(
            b,
            a.book_id == b.book_id
        ).filter(
            a.user_id == user_id
        ).order_by(
            a.saved_at.desc()
        )

        return {
            'data': [
                {
                    'book_id': book.book_id,
                    'title': book.title,
                    'authors': book.authors,
                    'description': book.description,
                    'pages': book.pages,
                    'date': book.date,
                    'thumbnail': book.thumbnail,
                    'url': book.url
                } for book in data
            ]
        }
    
    @classmethod
    def getBookFirstFavourite(cls, user_id, book_id):
        return cls.query.filter_by(user_id=user_id, book_id=book_id).first()