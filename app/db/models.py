from sqlalchemy import Column, Integer, String, Sequence, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from hashlib import sha1
from os import urandom

Base = declarative_base()


Membership = Table('membership', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.userid')),
    Column('role_id', Integer, ForeignKey('role.roleid'))
)


class Role(Base):
    __tablename__ = 'role'
    roleid = Column(Integer, Sequence('role_id_seq'), primary_key=True)
    name = Column(String(50))
    desc = Column(String(255))

    def __repr__(self):
        return "<Role(roleid={0}, name='{1}', desc='{2}')>".format(
            self.roleid,
            self.name,
            self.desc
        )


class User(Base):
    __tablename__ = 'user'
    userid = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    email = Column(String(255))
    password = Column(String(255))
    salt = Column(String(255))
    key = Column(String(255))
    posts = relationship("Post", backref='author')
    roles = relationship('Role', secondary='membership', backref='users')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.salt = urandom(16).encode('base64')
        self.key = urandom(32).encode('base64')
        self.set_password(password)

    def set_password(self, password):
        self.password = User.hash_password(password, self.salt)

    def check_password(self, password):
        return self.password == User.hash_password(password, self.salt)

    @staticmethod
    def hash_password(password, salt):
        _crypt = sha1()
        _crypt.update(salt)
        _crypt.update(password)
        return _crypt.hexdigest()

    @property
    def api_key(self):
        crypto = sha1()
        crypto.update(self.salt)
        crypto.update(self.password)
        crypto.update(self.key)
        return crypto.hexdigest()

    def is_in_role(self, role):
        for _role in self.roles:
            if role == _role.name:
                return True
        return False

    def __repr__(self):
        return "<User(userid={0}, name='{1}', email='{2}')>".format(
            self.userid, 
            self.name, 
            self.email
        )


class Post(Base):
    __tablename__ = 'post'
    postid = Column(Integer, Sequence('post_id_seq'), primary_key=True)
    title = Column(String(50))
    body = Column(Text)
    author_id = Column(Integer, ForeignKey('user.userid'))

    def __repr__(self):
        
        return "<Post(postid={0}, title='{1}', author='{2}')>".format(
            self.postid, 
            self.title, 
            (self.author.name if self.author else 'Unknown')    
        )

#if __name__ == "__main__":
    #from sqlalchemy import create_engine
    #engine = create_engine('sqlite:///:memory:')
    #r = Role(name='admin', desc='An admin group')
    #print(r)
