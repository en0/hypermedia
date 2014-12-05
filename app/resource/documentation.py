from app.resource import ResourceBase
from app.resource.errors import NotFoundException
from flask import abort, make_response
from xml.sax.saxutils import escape

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
                methods[method] = fn.__doc__
        
        return { 
            "key" : key, 
            "Description" : r.__doc__,
            "route" : ", ".join(uri),
            "methods": methods,
        }

    def as_html(data, code, headers):
        methods = ""
        for m,d in data['methods'].items():
            methods += """
                <div class='method'>
                    <h2>{method_name}</h2>
                    <pre>{method_desc}</pre>
                </div>""".format(method_name=escape(m), method_desc=escape(d))
    
        body = """
            <h1>API Documentation - {key}</h1>
                <p>{summary}</p>
                <p>Route: {route}</p>
                <div class='methods'>{methods}</div>
        """.format(
            key=escape(data['key']),
            summary=escape(data['Description']),
            methods=methods,
            route=escape(data['route']),
        )

        style = """
            .method {
                border: solid 1px #aaa;
                border-radius: 10px;
                padding: 10px;
                margin: 20px;
                background-color: #efefef;
            }"""

        document = """
            <html>
                <head>
                    <title>APIDOC - {key}</title>
                    <style>{style}</style>
                </head>
                <body>{body}</body>
            </html>
        """.format(
            key=escape(data['key']),
            body=body,
            style=style
        )

        return make_response(document)

    representations = {
        'text/html' : as_html
    }

