from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship

from database import Base
import datetime
from models.user import User

epoch = datetime.datetime.utcfromtimestamp(0)


class Food(Base):
    __tablename__ = 'food'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), unique=False)
    type = Column(String(100), unique=False)
    title = Column(String(100), unique=False)
    timestamp = Column(DateTime(timezone=False), unique=False, default=datetime.datetime.now)
    score = Column(Integer, unique=False)
    picture = Column(BYTEA, unique=False)
    grams = Column(Numeric, unique=False)

    user = relationship('User', foreign_keys='Food.user_id')

    def __init__(self, user_id=None, type=None, title=None, timestamp=None, score=None, picture=None, grams=None):
        self.user_id = user_id
        self.type = type
        self.title = title
        if title is not None:
            self.title = title.decode("UTF-8")
        self.timestamp = timestamp
        self.score = score
        self.picture = picture
        self.grams = grams

    def __repr__(self):
        return '<Food ' + str(self.id) + ' %r>' % self.title

    def get_dict(self):
        return dict(id=self.id, user_id=self.user_id, type=self.type, title=self.title, timestamp=self.timestamp,
                    timestamp_1970=(self.timestamp - epoch).total_seconds(), score=self.score, picture=self.picture,
                    grams=float(self.grams))

    def get_dict_without_picture(self):
        return dict(id=self.id, user_id=self.user_id, type=self.type, title=self.title, timestamp=self.timestamp,
                    timestamp_1970=(self.timestamp - epoch).total_seconds(), score=self.score, grams=float(self.grams))

    def get_dict_for_export(self):
        return dict(user_name=self.user.user_name, type=self.type, title=self.title.encode("UTF-8"), timestamp=self.timestamp,
                    score=self.score)
