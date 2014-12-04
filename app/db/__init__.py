from app.db import models
from app.db.models import Base as ModelBase

def initialize_for_debugging(engine):
    from sqlalchemy.orm import sessionmaker

    from hashlib import sha1
    from os import urandom

    Session = sessionmaker(bind=engine)

    create_schema(engine)
    _db_session = Session()

    _crypt = sha1()
    _u1_salt = 'R4tCY9YI+iCKT9oEuO+z+A==\n' #urandom(16).encode('base_64')
    _u1_key = 'jv6H2yQ0WAwAWKUpjo3MsIgGba5va6Inf+ttpIaU3PM=\n' #urandom(32).encode('base_64')
    _u_pass = 'I like statistics.'
    _crypt.update(_u1_salt)
    _crypt.update(_u_pass)
    _u1_hash = _crypt.hexdigest()

    _crypt = sha1()
    _u2_salt = _u1_salt #urandom(16).encode('base_64')
    _u2_key = _u1_key #urandom(32).encode('base_64')
    _u_pass = 'I like drawing.'
    _crypt.update(_u2_salt)
    _crypt.update(_u_pass)
    _u2_hash = _crypt.hexdigest()

    _u = models.User(name='Darrell Huff', email='dh@email.com', password=_u1_hash, salt=_u1_salt, key=_u1_key)
    _u2 = models.User(name='Irving Geis', email='ig@email.com', password=_u2_hash, salt=_u2_salt, key=_u2_key)

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
    _p3 = models.Post(
        title='Something goofy',
        body='Just cleaning the floor. Nothing to see here. Move along.',
        author=_u2
    )
    _db_session = Session()
    _db_session.add(_u)
    _db_session.add(_u2)
    _db_session.add(_p1)
    _db_session.add(_p2)
    _db_session.add(_p3)
    _db_session.commit()
    _db_session.close()


def create_schema(engine):
    ModelBase.metadata.create_all(engine)


__all__ = [
    'models',
    'ModelBase',
    'initialize_for_debugging',
    'create_schema',
]
