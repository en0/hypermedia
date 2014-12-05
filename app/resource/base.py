from flask.ext.restful import Resource
from flask import abort, g
from core.hm import Hypermedia
from app.resource.errors import NotFoundException, NotAuthorizedException
from app.resource.errors import MethodNotAllowedException, ForbiddenException
from functools import wraps

class ResourceBase(Hypermedia, Resource):
    """ The Base resource used by Flask as a hypermedia object """

    def dispatch_request(self, *args, **kwargs):

        try:
            return super(ResourceBase, self).dispatch_request(*args, **kwargs)
        except NotAuthorizedException:
            abort(401)
        except ForbiddenException:
            abort(403)
        except NotFoundException:
            abort(404)
        except MethodNotAllowedException:
            abort(405)

    @staticmethod
    def authority_required(layer, **params):
        def _authentication(fn):
            @wraps(fn)
            def _authentication_wrapper(*args, **kwargs):

                if g.authority.authenticated:
                    return fn(*args, **kwargs)
                else:
                    raise NotAuthorizedException()
            return _authentication_wrapper

        def _authorization(fn):
            @wraps(fn)
            def _authorization_wrapper(*args, **kwargs):
                for role in params.get('roles', []):
                    if g.authority.is_in_role(role):
                        return fn(*args, **kwargs)
                raise NotAuthorizedException()

            return _authorization_wrapper

        layers = {
            'authentication' : _authentication,
            'authorization' : _authorization,
        }

        return layers[layer]
        
