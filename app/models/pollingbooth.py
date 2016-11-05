from .. import db
import datetime


class PollingBooth(db.Model):
    __tablename__ = 'pollingbooth'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(64))
    zipCode = db.Column(db.Integer)
    people = db.relationship('User', backref='pollingbooth', lazy='dynamic')
    wait_times = db.relationship('WaitTime', backref='pollingidbooth', lazy='dynamic')

    def __init__(self, address):
        self.address = address
        self.zipCode = int(address.split()[-1])