import base64
import json
from urllib2 import BaseHandler, Request
import urlparse

class GoProxyHandler(BaseHandler):
    # Proxies must be in front
    handler_order = 100

    def __init__(self, proxy_url):
        # parse url to separate endpoint address and authorization code
        parsed_url = urlparse.urlparse(proxy_url)
        self.authorization_code = parsed_url.username
        self.proxy_endpoint = urlparse.urlunparse((parsed_url.scheme, parsed_url.hostname if parsed_url.port is None else "%s:%d" % (parsed_url.hostname, parsed_url.port), parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))

    def http_open(self, req):
        return self.proxy_open(req)

    def https_open(self, req):
        return self.proxy_open(req)

    def proxy_open(self, req):
        # filter out requests to our proxy
        if req.get_full_url() == self.proxy_endpoint:
            return None

        proxy_request = {
            'Code': self.authorization_code,
            'Verb': req.get_method(),
            'URI': req.get_full_url(),
            'Body':  base64.standard_b64encode(req.get_data() or ""),
            'Headers': req.headers
        }

        return self.parent.open(Request(self.proxy_endpoint, json.dumps(proxy_request)), timeout=req.timeout)
