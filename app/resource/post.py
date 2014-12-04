from app.resource import ResourceBase
from app.resource.errors import NotFoundException
from flask import abort

class PostBase(ResourceBase):
    """ Interaction with a single post resource """

    def get(self, postid=None):

        if not postid:
            self.load_all_from_db()
            return self.render_collection('_')

        else:
            self.load_from_db(postid)
            return self.render()

    @ResourceBase.authority_required('authentication')
    def put(self, postid=None):

        if not postid: abort(405)

        try:
            self.load_from_db(postid)
            self.update_from_request()
        except NotFoundException:
            self.create_from_request(postid)

        return self.render(), 201, { 'Location' : self.__uri__ }


    @ResourceBase.authority_required('authentication')
    def post(self, postid=None):

        if postid: abort(405)

        self.create_from_request()
        return self.render(), 201, { 'Location' : self.__uri__ }


    @ResourceBase.authority_required('authentication')
    def delete(self, postid):

        if not postid: abort(405)
        self.remove_from_db(postid)
        return None, 204

