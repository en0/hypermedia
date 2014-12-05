from app.db import models
from app.db.models import Base as ModelBase

def initialize_for_debugging(engine):
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)

    create_schema(engine)
    _db_session = Session()

    _r1 = models.Role(name='administrator', desc='Global Administrator')

    _u = models.User(
        name='Darrell Huff', 
        email='dh@email.com', 
        password='I like statistics.'
    )

    _u.roles.append(_r1)

    _u2 = models.User(
        name='Irving Geis', 
        email='ig@email.com', 
        password='I like drawing.',
    )

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
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    ModelBase.metadata.create_all(engine)
    _db_session = Session()
    _default_role = models.Role(roleid='1', name='user', desc='General user')
    _db_session.add(_default_role)


__all__ = [
    'models',
    'ModelBase',
    'initialize_for_debugging',
    'create_schema',
]
