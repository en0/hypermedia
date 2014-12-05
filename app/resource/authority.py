from app.resource import ResourceBase
from app.resource.errors import NotFoundException, NotAuthorizedException, MethodNotAllowedException
from flask import abort

class AuthorityBase(ResourceBase):
    """ The resource used by Flask as a hypermedia object """

    def post(self):
        self.load_from_request()
        return self.render()

