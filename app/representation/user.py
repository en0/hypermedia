## Hypermedia Library
from core.registrar import key as register, fns as representations
from core.hm import HypermediaFactory

## App resources
from app.resource import ResourceBase
import app.representation
from app.db import models

## Flask Library
from flask import g
from flask.ext.restful import reqparse

## Errors
from app.resource.errors import NotFoundException, NotAuthorizedException, MethodNotAllowedException, ForbiddenException


UserBaseV1 = HypermediaFactory(
    base=ResourceBase,
    class_name="UserBaseV1",
    resource_format="/v1.0/user/{userid}",
    resource_route=[ "/v1.0/user/<int:userid>", "/v1.0/user/" ],
    doc_key="v1.0-user",
    doc_uri="/docs/v1.0-user",
    public_fields=['name','email'],
    private_fields=['userid']
)


@register('v1.0-user')
class UserV1(UserBaseV1):
    """Represents a user"""

    def __init__(self):
        """ Create an instance of the User representation. 

        super.__init__ is called after reqparse args are configured.
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location = 'json')
        self.reqparse.add_argument('email', type=str, location = 'json')
        self.reqparse.add_argument('password', type=str, location = 'json')
        super(UserV1, self).__init__()
        self._n = None
        self._e = None
        self._i = None
        self.db_ref = None

    def load_from_db(self, userid):
        """ Loads and fills a single record into the current representation.

        self.load is called to fill the representation with the discovered database
        record.

        Arguments:
            userid - The identity of the user to load.

        Raises:
            NotFoundException - if the postid is not valid.
        """
        u = g.db.query(models.User).filter(models.User.userid == userid).first()
        self.db_ref = u
        if not u: raise NotFoundException()
        self.load(u)


    def load_all_from_db(self):
        """ Load all users in the system and add them to the '_' embedded object.

        This embedded object can be rendered as an array of post representations using
        the hypermedia.render_collection function. 
        """
        for u in g.db.query(models.User):
            _u = UserV1()
            _u.load(u, depth=0)
            self.add_rel_collection("_", _u, embedded=True)


    def update_from_request(self):
        """ Update the database record from the request body.

        It is expected the that existing record is already loaded. The update process
        will update both the database record as well as the representation fields.
        database changes are commited in this process.

        Raises:
            ForbiddenException - if the target user is not the same as the authenticated user.
        """
        if self.db_ref != g.authority.user: raise ForbiddenException
        _update = self.reqparse.parse_args()
        self._n = self.db_ref.name = _update.name if _update.name else self.db_ref.name
        #self._e = self.db_ref.email = _update.email if _update.email else self.db_ref.email
        g.db.commit()


    def remove_from_db(self, userid):
        """ Remove a User from the database.

        The record is reomved from the database and the changes are commited in this
        action. No data is loaded into the current representation.

        Arguments:
            userid - The identity of the user to remove.

        Raises:
            ForbiddenException - If the current user is the same as the user to be removed
            NotFoundException - if the requested userid is not valid.
        """
        u = g.db.query(models.User).filter(models.User.userid == userid).first()
        self.db_ref = u
        if not u: raise NotFoundException()
        if u == g.authority.user: raise ForbiddenException()
        g.db.delete(u)
        g.db.commit()


    def create_from_request(self):
        """ Create a new database record using the values in the request body 

        The representation is loaded after the new database record is created.
        """
        _data = self.reqparse.parse_args()
        self.db_ref = models.User(**_data)
        g.db.add(self.db_ref)
        g.db.commit()
        self.load()


    def load(self, entity=None, depth=1):
        """ fill the content of this object from a database entry

        Arguments:
            entity - The object containing the details of the user.
            depth  - The recursion depth to load embeded and linked resources (Optional)
        """
        if entity == None: entity = self.db_ref
        self._n = entity.name
        self._e = entity.email
        self._i = entity.userid
        if depth <= 0: return
        for p in entity.posts:
            _post = app.representation.post.PostV1()
            _post.load(p, depth=depth)
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


    # :meth: hints for FLASK and APIDOC
    methods = [ 'GET', 'PUT', 'POST', 'DELETE' ]

    def get(self, userid=None):
        """ This method will return the state of one or more user representations.

        Two formats of the data are represented in this method.
        - List of all users, if the userid is not provided.
        - Specific user, if the userid is provided and valid.

        Arguments:
            userid - The identity of a specific user. (Optional)

        Raises:
            NotFoundException(404) - if the requested userid does not exist.

        Returns:
            200 (OK) on success.

        Presented Format:
            ** userid Provided **
            {
                "_embedded" : {
                    "v1.0-post:posts" : [ ... ]
                },
                "_links": {
                    "v1.0-user:self": {
                        "href": "/** URI to this user **/"
                    }
                }, 
                "email": "/** The email address of this user **/", 
                "name": "/** The name of this user **/"
            }

        Presented Format:
            ** No userid Provided **
            [
                {
                    "_links": {
                        "v1.0-user:self": {
                            "href": "/** URI to this user **/"
                        }
                    }, 
                    "email": "/** The email address of this user **/", 
                    "name": "/** The name of this user **/"
                },

                { ... }
            ]
        

        Relationships:
            self - Contains a href to the uri of the current object.

        Embedded Representations:
            posts - The posts authored by this user. See v1.0-post for more details.
        """
        if not userid:
            self.load_all_from_db()
            return self.render_collection('_')

        else:
            self.load_from_db(userid)
            return self.render()


    @ResourceBase.authority_required('authentication')
    def put(self, userid=None):
        """ This method will update a specific user.

        v1.0 api only allows users to update themselfs. This method can be used
        to change the name or password of a user. The email field will not accept
        changes.

        Raises:
            NotFoundException (404) - If the requested user is not valid or does not exist.
            ForbiddenException (403) - If the target user is not the same as the authenticated user.
            NotAuthorizedException (401) - if the request is made by an unauthenticated user.

        Returns:
            201 (Created) on success.

        Expected Format:
            {
                "name" : "/** The new name of the user (optional) **/",
                "password" : "/** The new password for the user (optional) **/"
            }

        Note: 
            The API Key is associated with the users password. If a password is changed, the corresponding
            api key for that user will also be changed.
        """
        if not userid: raise NotFoundException()
        self.load_from_db(userid)
        self.update_from_request()
        return self.render(), 201, { 'Location' : self.__uri__ }


    def post(self, userid=None):
        """ This method will create a new user.

        POST can be used to create a new user. The userid will be generated by the server.
        The location header is set to the location of the new user resource and the representation
        is provided in the content body of the response.

        Raises:
            MethodNotAllowedException (405) - If the userid is provided. Use PUT method instead.

        Returns:
            201 (Created) on success.

        Expected Format:
            {
                "email" : "/** The email address used for the new user (Required). **/",
                "name" : "/** The name used for the new user (Required). **/",
                "password" : "/** The password for the new user (Required). **/"
            }

        Presented Format:
            {
                "_embedded" : {
                    "v1.0-post:posts" : [ ... ]
                },
                "_links": {
                    "v1.0-user:self": {
                        "href": "/** URI to this user **/"
                    }
                }, 
                "email": "/** The email address of this user **/", 
                "name": "/** The name of this user **/"
            }

        Relationships:
            self - Contains a href to the uri of the current object.

        Embedded Representations:
            posts - The posts authored by this user. See v1.0-post for more details.
        """
        if userid: raise MethodNotAllowedException()
        self.create_from_request()
        return self.render(), 201, { 'Location' : self.__uri__ }


    @ResourceBase.authority_required('authorization', roles=['administrator'])
    def delete(self, userid=None):
        """ This method will remove the specified user from the system.

        This action can only be performed by an administrator. This action cannot
        remove the authenticated user that is used to access this method. Basicly,
        Administrators can delete anybody but themselfs.

        Arguments:
            userid - The identity of the user to remove. (Required)

        Raises:
            NotAuthorizedException (401) - If the request is made by an unauthenticated user 
                                         - if the request is made by a user that is not in the administrator group.
            ForbiddenException (403) - If the authenticated user is the same as the target of the delete method.
            NotFoundException (404) - If the userid is not valid or does not exist.

        Returns:
            204 (No Content) on success.
        """
        if not userid: raise NotFoundException()
        self.remove_from_db(userid)
        return None, 204

