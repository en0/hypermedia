
from config import DevelopmentConfig as Config

from flask import Flask, request, g
from flask.ext.restful import Resource, Api

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.representation as rep


## Initialize database connection
engine = create_engine(Config.DATABASE_URI, echo=False)
Config.DbSession = sessionmaker(bind=engine)
Config.DbEngine = engine

## Install some fake data
def debug_data():
    import app.db.models as models
    models.Base.metadata.create_all(engine)

    _u = models.User(name='Darrell Huff', email='dh@email.com')
    _u2 = models.User(name='Irving Geis', email='ig@email.com')
    _p1 = models.Post(
        title='98.4% of Most Metics...', 
        body="Don't be a novelist --- be a statistician. Much more scope for the imagination.", 
        author=_u
    )
    _p2 = models.Post(
        title='6 or a Half Dozen',
        body='Proper treatment will cure a cold in seven days, but left to itself, a cold will hang on for a week.',
        author=_u
    )
    _db_session = Config.DbSession()
    _db_session.add(_u)
    _db_session.add(_u2)
    _db_session.add(_p1)
    _db_session.add(_p2)
    _db_session.commit()
    _db_session.close()


## Initialize uWSGI Service Module
app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)


## Install database middleware
@app.before_first_request
def before_frist_request():
    if Config.DEBUG:
        debug_data()


@app.before_request
def before_request():
    g.db = Config.DbSession()


@app.teardown_request
def after_request(x):
    if g.db: 
        g.db.close()


## Install Registered Routes
for label, resource, route in rep.next():
    print('Loading: {0} - {1}'.format(label, route))
    api.add_resource(resource, route)


## If running on the command line, Execute Listener
if __name__ == "__main__":
    app.run(host='0.0.0.0')

