from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(100), unique=True)
    first_name = Column(String(100), unique=False)
    year_born = Column(Integer, unique=False)
    fitbit_access_token = Column(String, unique=False)

    def __init__(self, user_name=None, first_name=None, year_born=None, fitbit_access_token=None):
        self.user_name = user_name
        self.first_name = first_name
        self.year_born = year_born
        self.fitbit_access_token = fitbit_access_token

    def __repr__(self):
        return '<User ' + str(self.id) + ' %r>' % self.user_name

    def get_dict(self):
        return {'id': self.id, 'user_name': self.user_name, 'first_name': self.first_name, 'year_born': self.year_born,
                'fitbit_access_token': self.fitbit_access_token}

