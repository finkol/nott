import ast
import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from models.user import User

epoch = datetime.datetime.utcfromtimestamp(0)


class Sleep(Base):
    __tablename__ = 'sleep'
    id = Column(Integer, primary_key=True)
    is_main_sleep = Column(Boolean, unique=True)
    log_id = Column(String, unique=False)
    efficiency = Column(Integer, unique=False)
    start_time = Column(DateTime(timezone=False), unique=False)
    duration = Column(Integer, unique=False)
    minutes_to_fall_asleep = Column(Integer, unique=False)
    minutes_asleep = Column(Integer, unique=False)
    minutes_awake = Column(Integer, unique=False)
    minutes_after_wakeup = Column(Integer, unique=False)
    awake_count = Column(Integer, unique=False)
    awake_duration = Column(Integer, unique=False)
    restless_count = Column(Integer, unique=False)
    restless_duration = Column(Integer, unique=False)
    time_in_bed = Column(Integer, unique=False)
    minute_data = Column(String, unique=False)
    date_of_sleep = Column(DateTime(timezone=False), unique=False)
    user_id = Column(Integer, ForeignKey(User.id), unique=False)

    user = relationship('User', foreign_keys='Sleep.user_id')

    def __init__(self, is_main_sleep=None, log_id=None, efficiency=None, start_time=None, duration=None,
                 minutes_to_fall_asleep=None, minutes_asleep=None, minutes_awake=None, minutes_after_wakeup=None,
                 awake_count=None, awake_duration=None, restless_count=None, restless_duration=None, time_in_bed=None,
                 minute_data=None, date_of_sleep=None, user_id=None):
        self.user_id = user_id
        self.date_of_sleep = date_of_sleep
        self.minute_data = minute_data
        self.restless_duration = restless_duration
        self.minutes_after_wakeup = minutes_after_wakeup
        self.minutes_awake = minutes_awake
        self.duration = duration
        self.start_time = start_time
        self.restless_count = restless_count
        self.efficiency = efficiency
        self.minutes_asleep = minutes_asleep
        self.awake_duration = awake_duration
        self.awake_count = awake_count
        self.minutes_to_fall_asleep = minutes_to_fall_asleep
        self.log_id = log_id
        self.is_main_sleep = is_main_sleep
        self.time_in_bed = time_in_bed

    def __repr__(self):
        return '<Sleep ' + str(self.id) + ' %r>' % self.log_id

    def get_dict(self):
        return {'restless_duration': self.restless_duration,
                'minutes_after_wakeup': self.minutes_after_wakeup,
                'minutes_awake': self.minutes_awake,
                'duration': self.duration,
                'start_time': str(self.start_time),
                'start_time_1970': (self.start_time - epoch).total_seconds(),
                'restless_count': self.restless_count,
                'efficiency': self.efficiency,
                'minutes_asleep': self.minutes_asleep,
                'awake_duration': self.awake_duration,
                'awake_count': self.awake_count,
                'minutes_to_fall_asleep': self.minutes_to_fall_asleep,
                'log_id': self.log_id,
                'time_in_bed': self.time_in_bed,
                'is_main_sleep': self.is_main_sleep,
                'minute_data': ast.literal_eval(self.minute_data),
                'date_of_sleep': str(self.date_of_sleep),
                'date_of_sleep_1970': (datetime.datetime.combine(self.date_of_sleep, datetime.datetime.min.time()) - epoch).total_seconds(),
                'user_id': self.user_id}

    def get_data_for_daily(self):
        return {'start_time': str(self.start_time),
                'start_time_1970': (self.start_time - epoch).total_seconds(),
                'efficiency': self.efficiency,
                'minutes_to_fall_asleep': self.minutes_to_fall_asleep,
                'time_in_bed': self.time_in_bed,
                'is_main_sleep': self.is_main_sleep,
                'minute_data': ast.literal_eval(self.minute_data),
                'date_of_sleep': str(self.date_of_sleep),
                'date_of_sleep_1970': (datetime.datetime.combine(self.date_of_sleep, datetime.datetime.min.time()) - epoch).total_seconds(),
                'user_id': self.user_id}

    def get_data_for_export(self):
        return {'start_timestamp': str(self.start_time),
                'efficiency': self.efficiency,
                'minutes_to_fall_asleep': self.minutes_to_fall_asleep,
                'time_in_bed': self.time_in_bed,
                'is_main_sleep': self.is_main_sleep,
                'date_of_sleep': str(self.date_of_sleep),
                'user_name': self.user.user_name}
