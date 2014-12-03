from core.registrar import key as register, fns as representations
from app.resource.user import UserBase
from core.hm import HypermediaFactory

## Import other representations
import app.representation

from app.db import models
from flask import g


UserBaseV1 = HypermediaFactory(
    base=UserBase,
    class_name="UserBase",
    resource_format="/v1.0/user/{userid}",
    resource_route="/v1.0/user/<int:userid>",
    doc_key="usr",
    doc_uri="http://docs.example.com/api/usr",
    public_fields=['name','email'],
    private_fields=['userid']
)


@register('UserV1')
class UserV1(UserBaseV1):
    def __init__(self):
        self._n = None
        self._e = None
        self._i = None

    def load_from_db(self, userid):
        u = g.db.query(models.User).filter(models.User.userid == userid).first()
        self.load(u)

    def load(self, entity, depth=1):
        self._n = entity.name
        self._e = entity.email
        self._i = entity.userid
        if depth <= 0: return
        for p in entity.posts:
            _post = app.representation.post.PostV1()
            _post.load(p, depth=depth)
            self.add_rel_collection('posts', _post, embedded=True)

    @property
    def name(self):
        return self._n

    @property
    def email(self):
        return self._e

    @property
    def userid(self):
        return self._i


