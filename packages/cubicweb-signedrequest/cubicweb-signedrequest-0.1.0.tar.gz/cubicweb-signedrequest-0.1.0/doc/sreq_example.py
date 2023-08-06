import hmac
import urllib2
from datetime import datetime
from json import load

"""
A very simple example script showing how to forge a signed HTTP
request using a token.

You may test this by creating and starting an instance ot this
signedrequest cube (which is useless besides from this testing
purpose), add a 'toto' CWUser, and create Token using this 'toto' user
credentials (in the web UI).

You may then use this token to make HTTP requests as the 'toto' user:

python misc/sreq_example.py "http://perseus:8080/view?rql=rql%3ACWUser+X&vid=ejsonexport" mytoken3 2cc4e3a337b948139668c1f81bfc3cc49969dd5971cf4f2fb509a046e1dea244ccbb77fe8ab44fdcaf8d50d53731735c558b21b97133425088f13186fe76ae1e
[{u'__cwetype__': u'CWUser',
  u'creation_date': u'2013/07/29 15:51:34',
  u'cwuri': u'None6',
  u'eid': 6,
  u'firstname': None,
  u'last_login_time': u'2013/07/29 17:09:49',
  u'login': u'admin',
  u'modification_date': u'2013/07/29 17:09:49',
  u'surname': None,
  u'upassword': None},
 {u'__cwetype__': u'CWUser',
  u'creation_date': u'2013/07/29 15:55:23',
  u'cwuri': u'http://perseus:8080/736',
  u'eid': 736,
  u'firstname': u'Toto',
  u'last_login_time': u'2013/07/29 17:14:36',
  u'login': u'toto',
  u'modification_date': u'2013/07/29 17:14:36',
  u'surname': u'Toto',
  u'upassword': None}]

"""

def sign(req, token):
    headers_to_sign = ('Content-MD5', 'Content-Type', 'Date')
    method = req.get_method()
    url = req.get_full_url()
    get_header = lambda field: req.get_header(field, '')
    to_sign = method + url + ''.join(map(get_header, headers_to_sign))
    return hmac.new(token, to_sign).hexdigest()

def get(url, token_id, token):
    req = urllib2.Request(url,
                          headers={'Accept': 'text/plain',
                                   'Date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')})
    req.add_header('Authorization', 'Cubicweb %s:%s' % (token_id, sign(req, token)))
    return urllib2.urlopen(req)

if __name__ == "__main__":
    import sys, pprint
    if len(sys.argv) != 4:
        print "3 arguments expected: url token_id and token"
        sys.exit(1)
    url, token_id, token = sys.argv[1:]
    pprint.pprint(load(get(url, token_id, token)))
