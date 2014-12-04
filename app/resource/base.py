from flask.ext.restful import Resource
from flask import abort, g
from core.hm import Hypermedia
from app.resource.errors import NotFoundException, NotAuthorizedException

class ResourceBase(Hypermedia, Resource):
    """ The Base resource used by Flask as a hypermedia object """

    def dispatch_request(self, *args, **kwargs):

        try:
            return super(ResourceBase, self).dispatch_request(*args, **kwargs)
        except NotFoundException:
            abort(404)
        except NotAuthorizedException:
            abort(403)

    @staticmethod
    def authority_required(layer, **kwargs):
        def _authentication(fn):
            def _authentication_wrapper(*args, **kwargs):

                if g.authority.authenticated:
                    return fn(*args, **kwargs)
                else:
                    raise NotAuthorizedException()
            return _authentication_wrapper

        def _authorization(fn):
            def _authorization_wrapper(*args, **kwargs):

                ## We would want to check roles here.
                ## Something like this:
                for role in kwargs.get('roles', []):
                    if g.authority.is_in_role(role):
                        return fn(*args, **kwargs)
                raise NotAuthorizedException()

            return _authorization_wrapper(*args, **kwargs)

        layers = {
            'authentication' : _authentication,
            'authorization' : _authorization,
        }

        return layers[layer]
        
