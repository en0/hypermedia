import core.representation as rep
from core.db import fakedb

from pprint import pprint as pp
import json

def app(env, start_response):
	start_response('200 OK', [('Content-Type', 'application/json')])
	return "{'hello':'world'}"

if __name__ == "__main__":
    u1 = rep.user.UserV1()
    u1.load(fakedb['users']['1234'])
    o = u1.__render__()
    print(json.dumps(o, indent=2, sort_keys=True))

