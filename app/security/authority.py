from app.db import models
from flask import g
from base64 import b64encode

class Authority(object):
    def __init__(self):
        self._authenticated = False
        self._record = None

    def _get_record_by_email(self, email):
        record = g.db.query(models.User).filter(models.User.email == email).first()
        return record

    def authenticate_with_key(self, email, key):
        record = self._get_record_by_email(email)
        ## For debugging:
        if not record: return
        self.show_auth_token(record)
        if not key == record.api_key: return
        self._authenticated = True
        self._record = record

    def authenticate_with_password(self, email, password):
        record = self._get_record_by_email(email)
        if not record: return
        if not record.check_password(password): return
        self._authenticated = True
        self._record = record

    def is_in_role(self, role):
        if not self._authenticated: return False
        return self._record.is_in_role(role)
        
    @property
    def authenticated(self):
        return self._authenticated

    @property
    def user(self):
        return self._record

    @property
    def authority_token(self):
        if self.authenticated:
            token = ":".join([self._record.email, self._record.api_key])
            return b64encode(token.encode('utf-8')).decode('utf-8')

    def show_auth_token(self, record):
        token = ":".join([record.email, record.api_key])
        print('Your API Key is:', b64encode(token.encode('utf-8')))

