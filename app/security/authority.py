from os import urandom
from hashlib import sha1
from app.db import models
from flask import g

class Authority(object):
    def __init__(self):
        self._authenticated = False
        self._record = None

    def _get_record_by_email(self, email):
        record = g.db.query(models.User).filter(models.User.email == email).first()
        return record

    def authenticate_with_key(self, email, key):

        record = self._get_record_by_email(email)
        if not record: return
        kyhash = self.hash_key(record.password, record.key, record.salt)
        if not key == kyhash: return
        self._authenticated = True
        self._record = record

    def authenticate_with_password(self, email, password):

        record = self._get_record_by_email(email)
        if not record: return
        pwhash = self.hash_password(password, record.salt)
        if not pwhash == record.password: return
        self._authenticated = True
        self._record = record

    def hash_password(self, password, salt=None):
        if not salt: salt = urandom(16).encode('base_64')
        crypto = sha1()
        crypto.update(salt)
        crypto.update(password)
        return crypto.hexdigest()

    def pack_key(self):
        if not self._authenticated: return None
        kyhash = self.hash_key(self._record.password, self._record.key, self._record.salt)
        token = "{0}:{1}".format(self._record.email, kyhash)
        return token.encode('base_64')

    def hash_key(self, password_hash, key, salt):
        crypto = sha1()
        crypto.update(salt)
        crypto.update(password_hash)
        crypto.update(key)
        return crypto.hexdigest()
        
    @property
    def authenticated(self):
        return self._authenticated

    @property
    def user(self):
        return self._record

