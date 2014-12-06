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


## Create a hypermedia baseclass for the post object.
PostBaseV1 = HypermediaFactory(
    base=ResourceBase,
    class_name="PostBaseV1",
    resource_format="/v1.0/post/{postid}",
    resource_route=[ "/v1.0/post/<int:postid>", "/v1.0/post/" ],
    doc_key='v1.0-post',
    doc_uri="/docs/v1.0-post",
    public_fields=['title', 'body'],
    private_fields=['postid']
)

@register('v1.0-post')
class PostV1(PostBaseV1):
    """ Represents a Blog post entry. """

    def __init__(self):
        """ Create an instance of the Post representation. 

        super.__init__ is called after reqparse args are configured.
        """
        
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location = 'json')
        self.reqparse.add_argument('body', type=str, location = 'json')
        super(PostV1, self).__init__()
        self._t = None
        self._b = None
        self._i = None
        self.db_ref = None

    def _get_db_entity(self, postid):
        """ Locate the database entry for the given postid.

        The record is set into the representation's instance db_ref field.

        Arguments:
            postid - The identity of the post to be loaded.
        """
        p = g.db.query(models.Post).filter(models.Post.postid == postid).first()
        self.db_ref = p
        return p

    def remove_from_db(self, postid):
        """ Remove a post from the database.

        The record is reomved from the database and the changes are commited in this
        action. No data is loaded into the current representation.

        Arguments:
            Postid - The identity of the post to remove.

        Raises:
            ForbiddenException - If the current user does not own the post to be deleted.
        """
        p = self._get_db_entity(postid)
        if p:
            if p.author != g.authority.user: raise ForbiddenException()
            g.db.delete(p)
            g.db.commit()
        else:
            raise NotFoundException()

    def load_from_db(self, postid):
        """ Loads and fills a single record into the current representation.

        self.load is called to fill the representation with the discovered database
        record.

        Arguments:
            postid - The id used to locate the record to load from the database.

        Raises:
            NotFoundException - if the postid is not valid.
        """
        p = self._get_db_entity(postid)
        if p: self.load(p)
        else: raise NotFoundException()

    def load_all_from_db(self):
        """ Load all posts in the system and add them to the '_' embedded object.

        This embedded object can be rendered as an array of post representations using
        the hypermedia.render_collection function. The embedded object limits the representation
        to title only.
        """
        for e in g.db.query(models.Post):
            _p = PostV1()
            _p.load(e)
            self.add_rel_collection(
                '_', 
                _p, title='{title}'
            )

    def update_from_request(self):
        """ Update the database record from the request body.

        It is expected the that existing record is already loaded. The update process
        will update both the database record as well as the representation fields.
        database changes are commited in this process.

        Raises:
            ForbiddenException - if the target post is not owned by the current user.
        """
        if self.db_ref.author != g.authority.user: raise ForbiddenException()
        _update = self.reqparse.parse_args()
        self._t = self.db_ref.title = _update.title if _update.title else self.db_ref.title
        self._b = self.db_ref.body = _update.body if _update.body else self.db_ref.body
        g.db.commit()

    def create_from_request(self, postid=None):
        """ Create a new database record using the values in the request body 

        If no postid is provided, one will be generated. The representation is
        loaded after the new record is created.

        Arguments:
            postid - Create the resource with the provided postid (Optional)
        """
        _data = self.reqparse.parse_args()
        if postid: _data.postid = postid
        _new = models.Post(**_data)
        _new.author = g.authority.user
        g.db.add(_new)
        g.db.commit()
        self.load(_new)


    def load(self, entity, depth=1):
        """ fill the content of this object from a database entry

        Arguments:
            entity - The object containing the details of the post
            depth  - The recursion depth to load embeded and linked resources (Optional)
        """
        self._t = entity.title
        self._b = entity.body
        self._i = entity.postid if hasattr(entity, 'postid') else None

        if hasattr(entity, 'author'):
            _author = app.representation.user.UserV1()
            _author.load(entity.author, depth=depth-1)
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


    # :meth: hints for FLASK and APIDOC
    methods = [ 'GET', 'PUT', 'POST', 'DELETE' ]


    @ResourceBase.ifnonematch
    def get(self, postid=None):
        """ This method will return the state of one or more post representations.

            Two formats of the data are represented in this method.
            - List of all posts - If postid is not provided
            - Specific post if postid is provided and valid

            Arguments:
                postid - The identity of a specific post. (Optional)

            Raises:
                NotFoundException (404) - If the requested postid does not exist.

            Returns:
                200 (OK) on success

            Presented Format:
                ** Postid Provided **

                {
                    "_links": {
                        "v1.0-post:self": {
                            "href": "/*** URI to this post ***/
                        }, 
                        "v1.0-user:author": {
                            "href": "/*** URI of the author ***/
                            "name": "/*** Name of the author ***/
                        }
                    }, 

                    "body": "/*** The body of the blog post ***/"
                    "title": "/*** The title of the blog post ***/"
                }

            Presented Format: 
                ** No Postid Provided **

                [
                    {
                        "_links": {
                            "v1.0-post:self": {
                                "href": "/*** URI to this post ***/
                            }, 
                            "v1.0-user:author": {
                                "href": "/*** URI of the author ***/
                                "name": "/*** Name of the author ***/
                            }
                        }, 
    
                        "title": "/*** The title of the blog post ***/"
                    },

                    [...]

                ]
                    
        """
        if not postid:
            self.load_all_from_db()
            return self.render_collection('_')

        else:
            self.load_from_db(postid)
            return self.render()

    @ResourceBase.authority_required('authentication')
    @ResourceBase.ifmatch
    def put(self, postid=None, ifmatch=None):
        """ This method will create or update a specific post

            PUT can be used to update a specific URI OR to create a specific URI.
            If a given postid does not exist, the system will create the post with the given postid.
            postid MUST be of type, integer.

            Arguments:
                postid - The identity of the post to be updated. (Required)

            Raises:
                NotFoundException (404) - If the requested postid is not valid or does not exist.
                ForbiddenException (403) - If the authenticated user does not own the requested post.
                NotAuthorizedException (401) - If the the request is made but an unauthenticated user.

            Returns:
                201 (Created) on success.

            Expected Format:
                {
                    "body": "/*** The new body of the blog post (Optional) ***/"
                    "title": "/*** The new title of the blog post (Optional) ***/"
                }
        """
        if not postid: raise NotFoundException()
        try:
            self.load_from_db(postid)

            _current_data = self.render()
            if not ifmatch(_current_data):
                return None, 412, { 'Location' : self.__uri__ }

            self.update_from_request()
        except NotFoundException:
            self.create_from_request(postid)

        return self.render(), 201, { 'Location' : self.__uri__ }


    @ResourceBase.authority_required('authentication')
    def post(self, postid=None):
        """ This method will create a new post.

            POST can be used to create a new blog post. The postid will be generated by the server.
            The Location header is set to the location of the new post and the new post is provided
            in the content body of the response.

            Raises:
                NotAuthorizedException (401) - If the the request is made but an unauthenticated user.
                MethodNotAllowedException (405) - If postid is provided. Use PUT method instead.

            Returns:
                201 (Created) on success.

            Expected Format:
                {
                    "body": "/*** The new body of the blog post (Optional) ***/"
                    "title": "/*** The new title of the blog post (Optional) ***/"
                }

            Presented Format:
                {
                    "_links": {
                        "v1.0-post:self": {
                            "href": "/*** URI to this post ***/
                        }, 
                        "v1.0-user:author": {
                            "href": "/*** URI of the author ***/
                            "name": "/*** Name of the author ***/
                        }
                    }, 

                    "body": "/*** The body of the blog post ***/"
                    "title": "/*** The title of the blog post ***/"
                }
        """
        if postid: raise MethodNotAllowedException()
        self.create_from_request()
        return self.render(), 201, { 'Location' : self.__uri__ }


    @ResourceBase.authority_required('authentication')
    @ResourceBase.ifmatch
    def delete(self, postid, ifmatch=None):
        """ This method will remove the specified blog post from the system.

            Arguments:
                postid - The identity of the post removed. (Required)

            Raises:
                NotAuthorizedException (401) - If the the request is made by an unauthenticated user.
                ForbiddenException (403) - If the authenticated user does not own the requested post.
                NotFoundException (404) - If postid is not valid or does not exist.

            Returns:
                204 (No Content) on success.

        """
        self.load_from_db(postid)

        _current_data = self.render()
        if not ifmatch(_current_data):
            return None, 412, { 'Location' : self.__uri__ }

        self.remove_from_db(postid)
        return None, 204
