from store.db import db

class BookFavouriteModel(db.Model):
    __tablename__ = 'Book_Favourite'

    favbook_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.String(100), nullable=False)

    @classmethod
    def getAllBookFavourites(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()
    
    @classmethod
    def getBookFirstFavourite(cls, user_id, book_id):
        return cls.query.filter_by(user_id=user_id, book_id=book_id).first()