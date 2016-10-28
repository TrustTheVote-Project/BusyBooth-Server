from .. import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    hashVal = db.Column(db.String(64), index=True)
    polling_booth = db.Column(db.Integer, db.ForeignKey('pollingbooth.id'))
    is_admin = db.Column(db.String(64))

    def __init__(self, hashVal, polling_booth, is_admin):
        self.hashVal = hashVal
        self.polling_booth = polling_booth
        self.is_admin = is_admin


    def overview(self):
        return {
            "code": 0,
            "hashVal": self.hashVal,
            "booth_id": self.polling_booth.id,
            "is_admin": self.is_admin
        }
