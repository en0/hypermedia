from app.resource import ResourceBase
from app.resource.errors import NotFoundException, NotAuthorizedException, MethodNotAllowedException
from flask import abort

class UserBase(ResourceBase):
    """ The resource used by Flask as a hypermedia object """
    def get(self, userid=None):
        if not userid:
            self.load_all_from_db()
            return self.render_collection('_')

        else:
            self.load_from_db(userid)
            return self.render()


    @ResourceBase.authority_required('authentication')
    def put(self, userid=None):
        if not userid: raise MethodNotAllowedException()
        self.load_from_db(userid)
        self.update_from_request()
        return self.render(), 201, { 'Location' : self.__uri__ }


    def post(self, userid=None):
        if userid: abort(405)
        self.create_from_request()
        return self.render(), 201, { 'Location' : self.__uri__ }


    @ResourceBase.authority_required('authorization', roles=['administrator'])
    def delete(self, userid=None):
        if not userid: raise MethodNotAllowedException()
        self.remove_from_db(userid)
        return None, 204
            

