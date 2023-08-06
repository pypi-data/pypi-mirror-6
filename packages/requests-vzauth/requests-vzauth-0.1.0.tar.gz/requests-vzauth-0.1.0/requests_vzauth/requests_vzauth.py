import hmac
import hashlib

from datetime import datetime
from requests.auth import AuthBase
from base64 import b64encode

class vzAuth(AuthBase):
    """Verizon Cloud authentication handler for requests"""
    def __init__(self, secret, access, request, content_type=None):
        self.secret = secret
        self.access = access
        self.request = request
        if content_type:
            self.content_type = content_type
        else:
            self.content_type = ''
        self.timestamp = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    """Return a hashed request using the secret key"""
    def build_request(self, string, method):
        string = "%s\n%s\n%s\n\n%s\n" % (method, self.content_type, self.timestamp, string)
        signature = b64encode(hmac.new(key=self.secret, msg=string, digestmod=hashlib.sha256).digest())
        completed_signature = "CloudApi AccessKey=%s SignatureType=HmacSHA256 Signature=%s" % (self.access, signature)
        return completed_signature

    def __call__(self, r):
        if self.content_type:
            r.headers['Content-Type'] = self.content_type
        r.headers['x-tmrk-authorization'] = self.build_request(self.request, r.method)
        r.headers['Date'] = self.timestamp
        return r
