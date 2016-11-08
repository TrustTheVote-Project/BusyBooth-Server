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
from sqlalchemy import func
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
    #c = db.session.query(func.count(PollingBooth.id)).scalar()
    #uc = db.session.query(func.count(User.id)).scalar()
    #print("%d Booths" % c)
    #print("%d Users" % uc)
    db.drop_all()
    db.create_all()
    db.session.commit()

@manager.command 
def file_upload(filename):
    print db 
    users = []
    booths = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        totalrows = len(rows)
        for i, line in enumerate(rows):
            if i % 100 == 0:
              print("Row %d/%d" % (i+1, totalrows))
            boothAddress = line['Polling Booth']

            zipCode = boothAddress.split()[-1]
            if '-' in zipCode:
            	zipCode = zipCode.split('-')[0]
              
            hashVal = line['Hash']
            polling_place_supervisor = "false"
            if(line['PollingPlaceSupervisor'] == '1'):
                polling_place_supervisor = "true"

            booths.append((boothAddress, zipCode))
            users.append([hashVal, boothAddress, polling_place_supervisor])

    #Uniquiefy booths
    seen = set()
    unique_booth_list = [item for item in booths if item[0] not in seen and not seen.add(item[0])]
    unique_booth_hashes = [{'address': x[0], 'zipCode': x[1]} for x in unique_booth_list]
    
    
    
    #bulk insert booths
    print("Insert %d booths" % len(unique_booth_hashes))
    db.session.execute(PollingBooth.__table__.insert(), unique_booth_hashes) 
    db.session.commit()
    #c = db.session.query(func.count(PollingBooth.id)).scalar()
    #db.session.commit()
    #print c
    
    # Make a dict of booths
    booth_ids = {}
    rows = db.session.query(PollingBooth).all()
    for i, row in enumerate(rows):
      booth_ids[row.address] = row.id
    
    user_inserts = []
    totalusers = len(users)
    for i, user_arr in enumerate(users):
      if i % 100 == 0:
        print("Row %d/%d Users" % (i+1, totalusers))      
      user_inserts.append({
        'hashVal': user_arr[0],
        'polling_booth': booth_ids[user_arr[1]],
        'is_admin': user_arr[2],
      })
    
    print "Run users insert"
    n = 1000
    for i in xrange(0, len(user_inserts), n):
      print("Insert users %d-%d of %d" % (i, i+n, len(user_inserts)))
      ui_group = user_inserts[i:i + n]
      db.session.execute(User.__table__.insert(), ui_group) 
      db.session.commit()
    
    

    # # Creating the new_booth if it needs to be created.
    #         new_booth = PollingBooth.query.filter_by(address=boothAddress).first()
    #         if new_booth == None:
    #             new_booth = PollingBooth(
    #                 address = boothAddress
    #             )
    #             db.session.add(new_booth)
    #             db.session.commit()
    #
    #         # Creating the new_user if it needs to be created.
    #         if User.query.filter_by(hashVal=hashVal).first() == None:
    #             new_user = User(
    #                 hashVal = hashVal,
    #                 polling_booth = new_booth.id,
    #                 is_admin = polling_place_supervisor
    #             )
    #             db.session.add(new_user)
    #             db.session.commit()


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
