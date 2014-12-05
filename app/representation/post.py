from app.resource.post import PostBase
from core.registrar import key as register, fns as representations
from app.resource.errors import NotFoundException, NotAuthorizedException
from core.hm import HypermediaFactory

## Import other representations
import app.representation

from app.db import models
from flask import g
from flask.ext.restful import reqparse


PostBaseV1 = HypermediaFactory(
    base=PostBase,
    class_name="PostBase",
    resource_format="/v1.0/post/{postid}",
    resource_route=[ "/v1.0/post/<int:postid>", "/v1.0/post/" ],
    doc_key='v1.0-post',
    doc_uri="/docs/v1.0-post",
    public_fields=['title', 'body'],
    private_fields=['postid']
)

@register('v1.0-post')
class PostV1(PostBaseV1):
    """ Represents a Blog post entry. """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location = 'json')
        self.reqparse.add_argument('body', type=str, location = 'json')
        super(PostV1, self).__init__()
        self._t = None
        self._b = None
        self._i = None
        self.db_ref = None

    def _get_db_entity(self, postid):
        p = g.db.query(models.Post).filter(models.Post.postid == postid).first()
        self.db_ref = p
        return p

    def remove_from_db(self, postid):
        p = self._get_db_entity(postid)
        if p:
            g.db.delete(p)
            g.db.commit()
        else:
            raise NotFoundException()

    def load_from_db(self, postid):
        p = self._get_db_entity(postid)
        if p: self.load(p)
        else: raise NotFoundException()

    def load_all_from_db(self):
        for e in g.db.query(models.Post):
            _p = PostV1()
            _p.load(e)
            self.add_rel_collection(
                '_', 
                _p, title='{title}', 
                body='{body:.50}...'
            )

    def update_from_request(self):
        if self.db_ref.author != g.authority.user: raise NotAuthorizedException
        _update = self.reqparse.parse_args()
        self._t = self.db_ref.title = _update.title if _update.title else self.db_ref.title
        self._b = self.db_ref.body = _update.body if _update.body else self.db_ref.body
        g.db.commit()

    def create_from_request(self, postid=None):
        _data = self.reqparse.parse_args()
        if postid: _data.postid = postid
        _new = models.Post(**_data)
        _new.author = g.authority.user
        g.db.add(_new)
        g.db.commit()
        self.load(_new)

    def load(self, entity, depth=1):
        self._t = entity.title
        self._b = entity.body
        self._i = entity.postid if hasattr(entity, 'postid') else None

        if hasattr(entity, 'author'):
            _author = app.representation.user.UserV1()
            _author.load(entity.author, depth=depth-1)
            self.add_rel('author', _author, name='{name}')

    @property
    def title(self):
        return self._t

    @property
    def body(self):
        return self._b

    @property
    def postid(self):
        return self._i

