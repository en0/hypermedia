from app.resource.post import PostBase
from core.registrar import key as register, fns as representations
from core.hm import HypermediaFactory

## Import other representations
import app.representation

from app.db import models
from flask import g


PostBaseV1 = HypermediaFactory(
    base=PostBase,
    class_name="PostBase",
    resource_format="/v1.0/post/{postid}",
    resource_route="/v1.0/post/<int:postid>",
    doc_key='pst',
    doc_uri='http://docs.example.com/api/pst',
    public_fields=['title', 'body'],
    private_fields=['postid']
)


@register('PostV1')
class PostV1(PostBaseV1):
    def __init__(self):
        self._t = None
        self._b = None
        self._i = None

    def load_from_db(self, postid):
        p = g.db.query(models.Post).filter(models.Post.postid == postid).first()
        self.load(p)

    def load(self, entity, depth=1):
        self._t = entity.title
        self._b = entity.body
        self._i = entity.postid
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

