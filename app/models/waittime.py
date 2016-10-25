from .. import db
import datetime

class WaitTime(db.Model):
    __tablename__ = 'waittime'
    id = db.Column(db.Integer, primary_key=True)
    elapsed = db.Column(db.Integer)
    polling_booth = db.Column(db.Integer, db.ForeignKey('pollingbooth.id'))
    end_time = db.Column(db.DateTime)
    # person = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, elapsed, polling_booth):
        self.elapased = elapsed
        self.polling_booth = polling_booth
        self.end_time = datetime.datetime.now()

    def overview(self):
        return {
            "code": 0,
            "elapsed": self.elapsed,
            "booth_id": self.polling_booth.id,
            "end_time": self.end_time
        }