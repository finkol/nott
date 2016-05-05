from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship

from database import Base
import datetime

from models.user import User

epoch = datetime.datetime.utcfromtimestamp(0)


class Activity(Base):
    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), unique=False)
    activity_type = Column(String(100), unique=False)
    start_time = Column(String(100), unique=False)
    end_time = Column(DateTime(timezone=False), unique=False, default=datetime.datetime.now)

    user = relationship('User', foreign_keys='Activity.user_id')

    def __init__(self, user_id=None, activity_type=None, start_time=None, end_time=None):
        self.user_id = user_id
        self.activity_type = activity_type
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return '<Activity ' + str(self.id) + ' %r>' % self.type

    def get_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'activity_type': self.activity_type,
                'end_time_1970': (self.end_time - epoch).total_seconds(),
                'start_time_1970': (self.start_time - epoch).total_seconds(), 'end_time': self.end_time,
                'start_time': self.start_time}

    def get_dict_for_export(self):
        return {'user_name': self.user.user_name, 'activity_type': self.activity_type,
         'end_datetime': self.end_time,
         'start_datetime': self.start_time}
