from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import BYTEA
from database import Base
import datetime


class Food(Base):
    __tablename__ = 'food'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    type = Column(String(100), unique=False)
    title = Column(String(100), unique=False)
    timestamp = Column(DateTime(timezone=False), unique=False, default=datetime.datetime.now)
    score = Column(Integer, unique=False)
    picture = Column(BYTEA, unique=False)
    grams = Column(Numeric, unique=False)

    def __init__(self, user_id=None, type=None, title=None, timestamp=None, score=None, picture=None, grams=None):
        self.user_id = user_id
        self.type = type
        self.title = title
        self.timestamp = timestamp
        self.score = score
        self.picture = picture
        self.grams = grams

    def __repr__(self):
        return '<Food ' + str(self.id) + ' %r>' % self.title

    def get_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'type': self.type, 'title': self.title, 'timestamp': self.timestamp,
                'score': self.score, 'picture': self.picture, 'grams': float(self.grams)}