import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base


class Sleep(Base):
    __tablename__ = 'sleep'
    id = Column(Integer, primary_key=True)
    is_main_sleep = Column(Boolean, unique=True)
    log_id = Column(Integer, unique=False)
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

    def __init__(self, is_main_sleep=None, log_id=None, efficiency=None, start_time=None, duration=None,
                 minutes_to_fall_asleep=None, minutes_asleep=None, minutes_awake=None, minutes_after_wakeup=None,
                 awake_count=None, awake_duration=None, restless_count=None, restless_duration=None, time_in_bed=None):
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
        'start_time': self.start_time,
        'restless_count': self.restless_count,
        'efficiency': self.efficiency,
        'minutes_asleep': self.minutes_asleep,
        'awake_duration': self.awake_duration,
        'awake_count': self.awake_count,
        'minutes_to_fall_asleep': self.minutes_to_fall_asleep,
        'log_id': self.log_id,
        'time_in_bed': self.time_in_bed,
        'is_main_sleep': self.is_main_sleep}




    