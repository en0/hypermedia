## Hypermedia Library
from core.registrar import key as register, fns as representations
from core.hm import HypermediaFactory

## App resources
from app.resource import ResourceBase
from app.security import Authority
import app.representation
from app.db import models

## Flask Library
from flask import g
from flask.ext.restful import reqparse

## Errors
from app.resource.errors import NotFoundException, NotAuthorizedException, MethodNotAllowedException, ForbiddenException


AuthorityBaseV1 = HypermediaFactory(
    base=ResourceBase,
    class_name="AuthorityBaseV1",
    resource_format="/v1.0/authority/",
    resource_route="/v1.0/authority/",
    doc_key="v1.0-auth",
    doc_uri="/docs/auth",
    public_fields=['token', 'header', 'pattern', 'status'],
    private_fields=[]
)

@register('v1.0-auth')
class AuthorityV1(AuthorityBaseV1):
    """ Used to retrieve the authority ticket for a user. """

    def __init__(self):
        """ Create an instance of the Authority representation. 

        super.__init__ is called after reqparse args are configured.
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, location = 'json')
        self.reqparse.add_argument('password', type=str, location = 'json')
        super(AuthorityV1, self).__init__()
        self.ref = None

    def load_from_request(self):
        """ Load the credentials from the request object and attempt to authenticate

        The instance field 'ref' is updated on this action with the Authority object
        and authentication with password is attempted.
        """
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

    methods = [ 'POST' ]

    def post(self):
        """ This method will authenticate a user.

        POST can be used to validate a user and retrieve the API Token used for future requests.
        This token is a base64 encoded packet containing the user's email address and api key.
        The format of this token is sutable for use with HTTP Basic Authentication and should be
        placed in the Authentication header for every request that required authorization.

        Returns:
            200 (OK) on success.

        Presented Format;
            {
                "_links": {
                    "v1.0-auth:self": {
                        "href": "/** **/"
                    }
                }, 
                "header": "/** The header the token should be placed for authenticated requests. **/"
                "pattern": "/** Pattern used to fill the header. **/"
                "status": "/** Success or Failed - State of authentication **/"
                "token": "/** The base64 encoded email:api key token used for authenticated requests. **/"
            }

            
        """
        self.load_from_request()
        return self.render()
