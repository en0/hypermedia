import core.representation
from core.hm import HypermediaFactory

PostBaseV1 = HypermediaFactory(
    class_name="PostBase",
    resource_format="/post/{postid}",
    doc_key='pst',
    doc_uri='http://docs.example.com/api/pst',
    public_fields=['title', 'body'],
    private_fields=['postid']
)

class PostV1(PostBaseV1):
    def __init__(self):
        self._t = None
        self._b = None
        self._i = None

    def load(self, entity, depth=1):
        self._t = entity['title']
        self._b = entity['body']
        self._i = entity['postid']
        if depth < 0: return
        _author = core.representation.user.UserV1()
        _author.load(entity['author'], depth=depth-1)
        self.add_rel('author', _author, name='{name}')

    @property
    def title(self):
        return self._t

    @property
    def body(self):
        return self._b

    @property
    def postid(self):
        return self._i

