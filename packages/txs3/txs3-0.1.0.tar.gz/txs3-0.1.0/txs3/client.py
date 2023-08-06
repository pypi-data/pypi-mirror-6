import xml.etree.ElementTree as etree
import urllib
import json

from twisted.web.client import readBody
from twisted.web.http_headers import Headers

from . import error, signing


class Operation(object):
    def __init__(self, client, method, name='', bucket_name=None, path='',
                 raw=False):
        self._client = client
        self._method = method
        self._name = name
        self._bucket_name = bucket_name
        self._path = path
        self._israw = raw

    def _responseToXML(self, response):
        d = readBody(response)
        d.addCallback(etree.fromstring)
        return d

    def __call__(self, bodyProducer=None, **kwargs):
        if self._name:
            kwargs[self._name] = ''
        uri = self._client._uri(self._bucket_name, self._path, **kwargs)
        d = self._client._agent.request(self._method, uri,
                                        bodyProducer=bodyProducer)
        if not self._israw:
            d.addCallback(self._responseToXML)
        return d


class S3Client(object):
    SERVICE = 's3'
    NS = 'http://s3.amazonaws.com/doc/2006-03-01/'

    bodyProcessors = {
        'application/xml': etree.fromstring,
        'application/json': json.loads,
        'application/x-bittorrent': None,
    }

    def __init__(self, reactor, access_key, secret_key, region):
        self._region = region
        signData = signing.SigningData(access_key, secret_key, region,
                                       self.SERVICE)
        self._agent = signing.SigningAgent(reactor, signData)
        self._host = 's3-{}.amazonaws.com'.format(region)

    def _uri(self, bucket, path, action, params):
        if bucket:
            host = '{}.{}'.format(bucket, self._host)
        else:
            host = self._host

        if path:
            path = urllib.quote(path.lstrip('/'))
        else:
            path = ''

        if params is None:
            params = {}

        if action:
            params[action] = ''

        if params:
            # Filter out None values
            params = {k: v for k, v in params.iteritems() if v is not None}
            params = urllib.urlencode(params)
            path = '{}?{}'.format(path, params)

        return 'https://{}/{}'.format(host, path)

    def makeRequest(self, bucket, key, method, action=None, params=None,
                    body=None, headers=None, processResponse=True,
                    responseContentType=None):
        uri = self._uri(bucket, key, action, params)
        if not headers:
            headers = {}
        if body and 'Content-Type' not in headers:
            headers['Content-Type'] = getattr(body, 'contentType', None)
        if hasattr(body, 'md5Hash') and 'Content-MD5' not in headers:
            headers['Content-MD5'] = body.md5Hash()
        headers = Headers({k: [v] for k, v in headers.iteritems()
                           if k and v is not None})
        d = self._agent.request(method, uri, headers, body)
        if processResponse:
            d.addCallback(self.processResponse, responseContentType)
        return d

    def _readResponseBody(self, response, contentType):
        try:
            processor = self.bodyProcessors[contentType]
        except KeyError:
            raise RuntimeError('Unknown content type: {}'.format(contentType))
        else:
            d = readBody(response)
            if processor is not None:
                d.addCallback(processor)
            return d

    def processResponse(self, response, contentType=None):
        if not contentType:
            try:
                contentType = response.headers.getRawHeaders('Content-Type')[0]
            except TypeError:
                contentType = None

        if response.code == 204 or response.code == 200 and not contentType:
            return
        elif response.code == 200:
            return self._readResponseBody(response, contentType)
        elif response.code // 100 in (3, 4, 5):
            assert contentType == 'application/xml'
            d = self._readResponseBody(response, contentType)
            d.addCallback(error.S3ResponseError.raiseFromXML)
            return d
        else:
            raise RuntimeError('Don\'t know how to handle this responde code: '
                               '{}'.format(response.code))

    @classmethod
    def ns(cls, *els):
        return '/'.join(('{{{}}}{}'.format(cls.NS, el) for el in els))

ns = S3Client.ns
etree.register_namespace(S3Client.SERVICE, S3Client.NS)
