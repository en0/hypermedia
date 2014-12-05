from core.registrar import key as register, fns as representations
from app.resource import AuthorityBase
from app.resource.errors import NotFoundException, NotAuthorizedException, ForbiddenException
from core.hm import HypermediaFactory

## Import other representations
import app.representation

from app.db import models
from flask import g
from flask.ext.restful import reqparse
from app.security import Authority


AuthorityBaseV1 = HypermediaFactory(
    base=AuthorityBase,
    class_name="AuthorityBase",
    resource_format="/v1.0/authority/",
    resource_route="/v1.0/authority/",
    doc_key="v1.0-auth",
    doc_uri="/docs/auth",
    public_fields=['token', 'header', 'pattern', 'status'],
    private_fields=[]
)

@register('v1.0-auth')
class AuthorityV1(AuthorityBaseV1):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, location = 'json')
        self.reqparse.add_argument('password', type=str, location = 'json')
        super(AuthorityV1, self).__init__()
        self.ref = None

    def load_from_request(self):
        creds = self.reqparse.parse_args()
        print(creds)
        self.ref = Authority()
        self.ref.authenticate_with_password(**creds)

    @property
    def token(self):
        if self.ref.authenticated:
            return self.ref.authority_token

    @property
    def header(self):
        if self.ref.authenticated:
            return 'Authorization'

    @property
    def pattern(self):
        if self.ref.authenticated:
            return '{HEADER}: Basic {TOKEN}'

    @property
    def status(self):
        if self.ref.authenticated:
            return 'Success'
        return 'Failed'

