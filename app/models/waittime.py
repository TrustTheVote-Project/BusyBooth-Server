from .. import db
import datetime

class WaitTime(db.Model):
    __tablename__ = 'waittime'
    id = db.Column(db.Integer, primary_key=True)
    elapsed = db.Column(db.Integer)
    end_time = db.Column(db.DateTime)
    polling_booth = db.Column(db.Integer, db.ForeignKey('pollingbooth.id'))
    
    def __init__(self, elapsed, polling_booth):
        self.elapsed = int(elapsed)
        self.end_time = datetime.datetime.now()
        self.polling_booth = polling_booth

    def overview(self):
        return {
            "code": 0,
            "elapsed": self.elapsed,
            "end_time": self.end_time,
            "booth_id": self.polling_booth.id
        }