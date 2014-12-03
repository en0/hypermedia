from app.resource import ResourceBase

class PostBase(ResourceBase):
    """ The resource used by Flask as a hypermedia object """
    def get(self, postid):
        self.load_from_db(postid)
        return self.render()

