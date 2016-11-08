#!/usr/bin/env python
import os

# Import settings from .env file. Must define FLASK_CONFIG
if os.path.exists('.env'):
    print('Importing environment from .env file')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


from app import create_app, db
from app.models import WaitTime, PollingBooth, User
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from config import TestingConfig
import time
import csv


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def drop_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@manager.command 
def file_upload(filename):
    print os.environ.get('DATABASE_URL') 
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        totalrows = len(rows)
        for i, line in enumerate(rows):
            if i % 100 == 0:
              print("Row %d/%d" % (i+1, totalrows))
            boothAddress = line['Polling Booth']
            hashVal = line['Hash']
            if(line['PollingPlaceSupervisor'] == '1'):
                polling_place_supervisor = "true"
            else:
                polling_place_supervisor = "false"



            # Creating the new_booth if it needs to be created.
            new_booth = PollingBooth.query.filter_by(address=boothAddress).first()
            if new_booth == None:
                new_booth = PollingBooth(
                    address = boothAddress
                )
                db.session.add(new_booth)
                db.session.commit()

            # Creating the new_user if it needs to be created.
            if User.query.filter_by(hashVal=hashVal).first() == None:
                new_user = User(
                    hashVal = hashVal,
                    polling_booth = new_booth.id,
                    is_admin = polling_place_supervisor
                )
                db.session.add(new_user)
                db.session.commit()


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
