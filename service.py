
from config import DevelopmentConfig as Config

from app.db import initialize_for_debugging, create_schema
from app.security import Authority
import app.representation as rep

## Flask
from flask import Flask, request, g, abort
from flask.ext.restful import Api
from flask.views import View

## Sql Alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


## Initialize database connection
engine = create_engine(Config.DATABASE_URI, echo=False)
Config.DbSession = sessionmaker(bind=engine)
Config.dbengine = engine


## Initialize uWSGI Service Module
app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)


@app.before_first_request
def before_frist_request():
    if Config.DEBUG:
        initialize_for_debugging(Config.dbengine)
    elif Config.CREATE_SCHEMA:
        create_schema(Config.dbengine)


@app.before_request
def before_request():
    g.db = Config.DbSession()
    g.authority = Authority()
    if request.authorization:
        g.authority.authenticate_with_key(
            request.authorization.get('username'),
            request.authorization.get('password')
        )

        if not g.authority.authenticated:
            ## Regardless if the target resource is restricted or not,
            ## They provided bad creds so we cannot allow this to continue
            abort(403)

@app.teardown_request
def after_request(x):
    if hasattr(g, 'db') and g.db: 
        g.db.close()


## Install Registered Routes
for label, resource, route in rep.next():
    print('Loading: {0} - {1}'.format(label, route))
    if type(route) == str: route = [route]
    api.add_resource(resource, *route)

## If running on the command line, Execute Listener
if __name__ == "__main__":
    app.run(host='0.0.0.0')

