from core.registrar import key as register, fns as representations
from app.resource import UserBase
from app.resource.errors import NotFoundException, NotAuthorizedException
from core.hm import HypermediaFactory

## Import other representations
import app.representation

from app.db import models
from flask import g
from flask.ext.restful import reqparse


UserBaseV1 = HypermediaFactory(
    base=UserBase,
    class_name="UserBase",
    resource_format="/v1.0/user/{userid}",
    resource_route=[ "/v1.0/user/<int:userid>", "/v1.0/user/" ],
    doc_key="usr",
    doc_uri="http://docs.example.com/api/usr",
    public_fields=['name','email'],
    private_fields=['userid']
)


@register('UserV1')
class UserV1(UserBaseV1):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location = 'json')
        self.reqparse.add_argument('email', type=str, location = 'json')
        super(UserV1, self).__init__()
        self._n = None
        self._e = None
        self._i = None
        self.db_ref = None

    def load_from_db(self, userid):
        u = g.db.query(models.User).filter(models.User.userid == userid).first()
        self.db_ref = u
        if not u: raise NotFoundException()
        self.load(u)


    def load_all_from_db(self):
        for u in g.db.query(models.User):
            _u = UserV1()
            _u.load(u, depth=0)
            self.add_rel_collection("_", _u, embedded=True)


    def update_from_request(self):
        if self.db_ref != g.authority.user: raise NotAuthorizedException
        _update = self.reqparse.parse_args()
        self._n = self.db_ref.name = _update.name if _update.name else self.db_ref.name
        self._e = self.db_ref.email = _update.email if _update.email else self.db_ref.email
        g.db.commit()
        

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


