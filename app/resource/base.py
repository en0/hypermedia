from flask.ext.restful import Resource
from core.hm import Hypermedia

class ResourceBase(Hypermedia, Resource):
    """ The Base resource used by Flask as a hypermedia object """
    pass
