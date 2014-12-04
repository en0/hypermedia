class Hypermedia(object):
    """ This class enforces the hypermedia format.

    If you want to extend this class, can inherit from it.
    To use this class or to use a class extended from this class, Use the
    HypermediaFactory and create your representation from it.

    Example:

    class UserBase(Hypermedia, Resource):
        def get(self, userid):
            self.load(userid)
            return self


    UserBaseV1 = HypermediaFactory(
        base=UserBase,
        class_name="UserBase",
        resource_format="/v1.0/user/{userid}",
        resource_route="/v1.0/user/<string:userid>",
        doc_key="usr",
        doc_uri="http://docs.example.com/api/usr",
        public_fields=['name','email'],
        private_fields=['userid']
    )


    class UserV1(UserBaseV1):
        def load(self, userid):
            ...

        @property
        def name(self):
            return self._name

        @property
        def email(self):
            return self._email

        @property
        def userid(self):
            return self._userid
    
    """
        
    def __init__(self):
        self.__rels__ = {}

    def add_rel(self, label, rel, embedded=False, **kwargs):

        self.__rels__[label] = {
            'as_collection' : False,
            'base_class' : type(rel),
            'as_embedded' : embedded,
            'link' : { 
                'rel' : rel, 
                'kwargs' : kwargs if not embedded else None 
            },
        }

    def add_rel_collection(self, label, rel, embedded=False, **kwargs):

        _collection_ = self.__rels__.get(label, {
            'as_collection' : True,
            'base_class' : type(rel),
            'as_embedded' : embedded,
            'link' : [],
        })

        if not _collection_['base_class'] == type(rel):
            raise TypeError("Relationship collections must be the same type")
        elif not _collection_['as_collection']:
            raise TypeError("Existing relationship is not a collection")
        else:
            _collection_['link'].append({ 
                'rel' : rel, 
                'kwargs' : kwargs if not embedded else None 
            })
            self.__rels__[label] = _collection_

    def render_collection(self, rel_label):
        ref = self.__rels__.get(rel_label, {'link':[]})
        ret = []

        for l in ref['link']:
            if ref['as_embedded']:
                ret.append(l['rel'].render())
            else:
                r = l['rel'].render()
                o = dict([(_k,_v) for _k, _v in r.items() if _k in ['_links', '_embedded']])
                for k,v in l['kwargs'].items():
                    d = l['rel'].get_field_values()
                    o[k] = v.format(**d)
                ret.append(o)
        return ret


    def render(self, with_curies=True):

        curies = [{ 'name' : self.__doc_key__, 'href' : self.__doc_uri__ }]
        _seen_curies = set([self.__doc_key__])
        embedded = {}

        links = { ":".join([self.__doc_key__,'self']) : { 'href' : self.__uri__ } }

        def __render_link__(ref):

            _rel = ref['rel']
            _kwa = ref['kwargs']

            _link = { 'href' : _rel.__uri__ }

            for k, v in _kwa.items():
                d = _rel.get_field_values()
                _link[k] = v.format(**d)

            return _link

        def __render_embedded__(ref):
            return ref['rel'].render(with_curies)

        def __format_rel__(ref, label, renderer):
            doc_key = ref['base_class'].__doc_key__

            if doc_key not in _seen_curies:
                _seen_curies.add(doc_key)
                curies.append({
                    'name' : doc_key,
                    'href' : ref['base_class'].__doc_uri__,
                })

            if ref['as_collection']:
                _obj = []
                for rel in ref['link']:
                    _obj.append(renderer(rel))

            else:
                _obj = renderer(ref['link'])

            return (
                "{0}:{1}".format(doc_key, label),
                _obj
            )

        for label, ref in self.__rels__.items():
            if ref['as_embedded']:
                key, obj = __format_rel__(ref, label, __render_embedded__)
                embedded[key] = obj
            else:
                key, obj = __format_rel__(ref, label, __render_link__)
                links[key] = obj

        obj = self.get_public_field_values()
        obj['_links'] = links

        if len(embedded) > 0: obj['_embedded'] = embedded
        if len(curies) > 0 and with_curies: links['curies'] = curies

        return obj
        


    def get_private_fields(self):
        return set(self.__sfields__)


    def get_public_fields(self):
        return set(self.__pfields__)


    def get_fields(self):
        return set(self.__pfields__ + self.__sfields__)


    def get_private_field_values(self):
        return dict([(k, getattr(self, k)) for k in self.get_private_fields()])


    def get_public_field_values(self):
        return dict([(k, getattr(self, k)) for k in self.get_public_fields()])


    def get_field_values(self):
        return dict([(k, getattr(self, k)) for k in self.get_fields()])


    @property
    def __uri__(self):
        d = self.get_field_values()
        return self.__resource_format__.format(**d)
        

    def __repr__(self):
        fl = []

        for field in self.get_fields(): fl.append(field+"='{"+field+"}'")
        d = self.get_field_values()
        return "<{0}({1})>".format(self.__cname__, ", ".join(fl)).format(**d)



def HypermediaFactory(class_name, base=Hypermedia, **kwargs):
    """ Create a new class type for a hypermedia object

    This will bind the resource defaults to the type of hypermedia object
    and allow the Hypermedia base class to render links properly.

    Arguments:
        class_name  - The name of the new class
        base        - The base class to use (default: Hypermedia)

    Keyword Arguments:
        resource_format - The format used to render the URI of the Hypermedia object.
                        - The format can refrence the name of a public or private field as if
                        - it is passed in a format command. ie: "/api/user/{userid}"
        resource_route  - The string used to identity the route to whatever services engine that is being used.
                        - ie: Flask or Bottle. A value such as "/resource/<string:id>"
        doc_key         - The key prefixed used when other classes refrence this as a link or embeded
        doc_uri         - The location of the documentation for this object.
        public_fields   - A list of names representing the public fields exposed as properties on this class.
        private_fields  - A list of names representing the private fields exposed as properties on this class.

    Throws:
        KeyError - If you are missing a keyward argument.
    """
        
    return type(class_name+"Class", (base,), {
        '__resource_format__' : kwargs['resource_format'],
        '__resource_route__' : kwargs['resource_route'],
        '__doc_key__' : kwargs['doc_key'],
        '__doc_uri__' : kwargs['doc_uri'],
        '__pfields__' : kwargs['public_fields'],
        '__sfields__' : kwargs['private_fields'],
        '__cname__': class_name,
    });

