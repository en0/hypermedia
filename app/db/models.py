from sqlalchemy import Column, Integer, String, Sequence, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    userid = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    email = Column(String(255))
    posts = relationship("Post", backref='author')

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
