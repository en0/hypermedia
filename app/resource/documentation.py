from app.resource import ResourceBase
from app.resource.errors import NotFoundException
from flask import abort, make_response, render_template

import app.representation

class DocumentationBase(ResourceBase):

    def __init__(self):
        super(DocumentationBase, self).__init__()
        self.reprs = {}
        for label, resource, route in app.representation.next():
            self.reprs[label] = (resource, route)

    def get(self, key):
        if not key in self.reprs: raise NotFoundException
        r,uri = self.reprs[key]

        if type(uri) == str: uri = [uri]

        methods = {}
        for method in r.methods:
            if hasattr(r, method.lower()):
                fn = getattr(r, method.lower())
                methods[method] = fn.__doc__ or ""
        
        return { 
            "key" : key, 
            "description" : r.__doc__ or "",
            "route" : ", ".join(uri),
            "methods": methods,
            "_links" : dict([(k,v[0].__doc__.strip(' ')) for k,v in self.reprs.items() if v[0].__doc__ != None])
        }

    def as_html(data, code, headers):

        x = render_template('documentation.html', ref=data)
        print(data['_links'])
        return make_response(x, code, headers)


    representations = {
        'text/html' : as_html
    }

