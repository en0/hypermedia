from flask.ext.restful import Resource
from flask import abort, g, make_response, request
from core.hm import Hypermedia
from app.resource.errors import NotFoundException, NotAuthorizedException
from app.resource.errors import MethodNotAllowedException, ForbiddenException
from functools import wraps

import json
from hashlib import sha1
from flask.ext.restful.utils import unpack

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
                raise ForbiddenException()

            return _authorization_wrapper

        layers = {
            'authentication' : _authentication,
            'authorization' : _authorization,
        }

        return layers[layer]


    @staticmethod
    def get_etag(body):
        """ Computes the etag for the data that is sent.
         
        The data should be a dictionay of your object and should not include codes or headers.
        
        Arguments:
            body - The dictionay of the response

        Returns:
            etag computed from the body
        """
        return sha1(json.dumps(body).encode('utf-8')).hexdigest()


    @staticmethod
    def ifnonematch(fn):
        """ Compute the etag and append it to the response headers.

        If the request has a conditional header `If-None-Match` present, then the wrapper
        will check to see if the data being returned is modified or not and send the appropriate
        response.
        """
        @wraps(fn)
        def _wrapper(*args, **kwargs):
            data, code, headers = unpack(fn(*args, **kwargs))
            etag = ResourceBase.get_etag(data)

            if 'If-None-Match' in request.headers and request.headers['If-None-Match'] == etag:
                return None, 304, headers

            headers['ETag'] = etag
            return data, code, headers
        return _wrapper


    @staticmethod
    def ifmatch(fn):
        """ Feeds a etag check function to the upstream function.

        The ifmatch function expects arguments: data. this is the dict type of your response.
        the etag will be computed and return true if the current etag matches the condition in the
        request or if the request contains no condition. It will return false if the condition
        does not match.

        Upstream function must except a key word argument for `ifmatch`
        """
        @wraps(fn)
        def _wrapper(*args, **kwargs):

            def __ifmatch(data):
                if 'If-Match' in request.headers:
                    etag = ResourceBase.get_etag(data)
                    return etag == request.headers['If-Match']
                return True
            
            kwargs['ifmatch'] = __ifmatch
            return fn(*args, **kwargs)

        return _wrapper

