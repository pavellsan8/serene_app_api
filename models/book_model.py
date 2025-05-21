from sqlalchemy import func
from sqlalchemy.orm import aliased

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

    @classmethod
    def getBookByFeelingId(cls, user_id):
        from models.questionnaire_model import QuestionnaireModel

        a = aliased(QuestionnaireModel)
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
            a.feeling_id == b.category_id,
        ).filter(
            a.user_id == user_id,
        ).order_by(
            func.random()
        ).all()

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