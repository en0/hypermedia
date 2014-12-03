from app.resource import ResourceBase

class UserBase(ResourceBase):
    """ The resource used by Flask as a hypermedia object """
    def get(self, userid):
        self.load_from_db(userid)
        return self.render()

