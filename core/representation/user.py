import core.representation
from core.hm import HypermediaFactory

UserBaseV1 = HypermediaFactory(
    class_name="UserBase",
    resource_format="/user/{userid}",
    doc_key="usr",
    doc_uri="http://docs.example.com/api/usr",
    public_fields=['name','email'],
    private_fields=['userid']
)

class UserV1(UserBaseV1):
    def __init__(self):
        self._n = None
        self._e = None
        self._i = None

    def load(self, entity, depth=1):
        self._n = entity['name']
        self._e = entity['email']
        self._i = entity['uid']
        if depth < 0: return
        for p in entity['posts']:
            _post = core.representation.post.PostV1()
            _post.load(p, depth=depth-1)
            self.add_rel_collection('posts', _post, embedded=True)

    @property
    def name(self):
        return self._n

    @property
    def email(self):
        return self._e

    @property
    def userid(self):
        return self._i

