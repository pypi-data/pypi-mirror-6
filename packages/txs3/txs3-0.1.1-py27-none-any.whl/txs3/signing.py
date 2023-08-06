import hmac
import hashlib
import re
import time
import urlparse
import urllib

from twisted.web.http_headers import Headers
from twisted.web.client import Agent, Request
from twisted.web._newclient import ChunkedEncoder
from twisted.web.http import datetimeToString as timestampToHttpString


def sign(key, payload, hex=False):
    auth = hmac.new(key, payload.encode('utf-8'), hashlib.sha256)
    return auth.hexdigest() if hex else auth.digest()


def uriEncode(s, encodeSlash=True):
    pattern = r'[^A-Za-z0-9._~-]' if encodeSlash else r'[^A-Za-z0-9._~/-]'

    def repl(m):
        return '%' + hex(ord(m.group(0)))[2:].upper()
    return re.sub(pattern, repl, s)


class SigningData(object):
    def __init__(self, access_key, secret_key, region, service):
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._service = service

    def makeSigner(self, timestamp=None):
        return TimestampedRequestSigner(self._access_key, self._secret_key,
                                        self._region, self._service,
                                        timestamp)


class TimestampedRequestSigner(object):
    def __init__(self, access_key, secret_key, region, service,
                 timestamp=None):
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._service = service
        self._timestamp = timestamp if timestamp else time.time()

    def _date(self):
        return time.strftime('%Y%m%d', time.gmtime(self._timestamp))

    def _credentials(self):
        return '{}/{}'.format(self._access_key, self._scope())

    def _scope(self):
        return '{}/{}/{}/aws4_request'.format(
            self._date(), self._region, self._service)

    def signRequest(self, request):
        request.headers.addRawHeader(
            'Date', timestampToHttpString(self._timestamp)
        )
        request.headers.addRawHeader(
            'x-amz-content-sha256', request.bodyHash()
        )
        headers, canonical = request.canonicalized()
        signingKey = self._signingKey()
        signingPayload = self._signingPayload(canonical)
        signature = sign(signingKey, signingPayload, True)
        authorization = (
            'AWS4-HMAC-SHA256 Credential={},SignedHeaders={},Signature={}'
            .format(self._credentials(), headers, signature)
        )
        request.headers.addRawHeader('Authorization', authorization)

        self._previousSignature = signature

    def signChunk(self, chunkData):
        signingKey = self._signingKey()
        signingPayload = self._signingChunkPayload(self._previousSignature,
                                                   chunkData)
        signature = sign(signingKey, signingPayload, True)
        self._previousSignature = signature
        return signature

    def _signingKey(self):
        kDate = sign(('AWS4' + self._secret_key).encode('utf-8'), self._date())
        kRegion = sign(kDate, self._region)
        kService = sign(kRegion, self._service)
        kSigning = sign(kService, 'aws4_request')
        return kSigning

    def _signingChunkPayload(self, previousSignature, chunkData):
        return '\n'.join([
            'AWS4-HMAC-SHA256-PAYLOAD',
            timestampToHttpString(self._timestamp),
            self._scope(),
            previousSignature,
            hashlib.sha256('').hexdigest(),
            hashlib.sha256(chunkData).hexdigest()
        ])

    def _signingPayload(self, canonical):
        return '\n'.join([
            'AWS4-HMAC-SHA256',
            timestampToHttpString(self._timestamp),
            self._scope(),
            hashlib.sha256(canonical).hexdigest()
        ])


class SigningChunkedEncoder(ChunkedEncoder, object):
    chunkSize = 64 * 1024

    def __init__(self, producer, transport, signer):
        super(SigningChunkedEncoder, self).__init__(transport)
        self._producer = producer
        self._signer = signer
        self._buffer = ''
        self._started = False
        self._finished = False
        self._paused = False

    def getChunkedLength(self):
        dataLength = self._producer.length
        chunksCount = dataLength / self.chunkSize
        remaining = dataLength % self.chunkSize

        def chunkOverhead(chunkSize):
            return len('{:x};chunk-signature='.format(chunkSize)) + 64 + 4

        lastChunkLength = chunkOverhead(remaining) if remaining else 0

        return (dataLength + chunksCount * chunkOverhead(self.chunkSize)
                + lastChunkLength + chunkOverhead(0))

    def startProducing(self):
        assert not self._started
        self._started = True
        self.transport.registerProducer(self, True)
        d = self._producer.startProducing(self)
        if self._paused:
            self._producer.pauseProducing()
        d.addCallback(self._done)
        return d

    def write(self, data):
        self._buffer += data
        while len(self._buffer) >= self.chunkSize and not self._paused:
            chunk = self._buffer[:self.chunkSize]
            self._buffer = self._buffer[self.chunkSize:]
            self._writeChunk(chunk)

    def _done(self, ignored):
        self._finished = True
        return ignored

    def unregisterProducer(self):
        if self._buffer:
            self._writeChunk(self._buffer)
        self._writeChunk('')
        self.transport.unregisterProducer()
        self._allowNoMoreWrites()

    def _writeChunk(self, data):
        signature = self._signer.signChunk(data)
        header = '{:x};chunk-signature={}\r\n'.format(len(data), signature)
        self.transport.writeSequence((header, data, '\r\n'))

    def stopProducing(self):
        self._producer.stopProducing()

    def pauseProducing(self):
        self._paused = True
        if self._started and not self._finished:
            self._producer.pauseProducing()

    def resumeProducing(self):
        self._paused = False
        if self._started:
            if not self._finished:
                self._producer.resumeProducing()
            self.write('')


class SigningRequest(Request, object):

    @classmethod
    def _construct(cls, signer, *args, **kwargs):
        self = super(SigningRequest, cls)._construct(*args, **kwargs)
        self._signer = signer
        return self

    def bodyHash(self):
        if self.bodyProducer:
            return 'STREAMING-AWS4-HMAC-SHA256-PAYLOAD'
        else:
            return hashlib.sha256('').hexdigest()

    def canonicalized(self):
        uri_query = self.uri.split('?', 1)
        uri = uriEncode(urllib.unquote(uri_query[0]), False)

        query = []
        if len(uri_query) > 1:
            qs = urlparse.parse_qsl(uri_query[1], keep_blank_values=True,
                                    strict_parsing=True)
            for k, v in sorted(qs):
                query.append(uriEncode(k) + '=' + uriEncode(v))
        query = '&'.join(query)

        vheaders = []
        keys = []
        for k, vs in sorted(self.headers.getAllRawHeaders(),
                            key=lambda h: h[0].lower()):
            keys.append(k.lower())
            for v in vs:
                vheaders.append(k.lower() + ':' + v.strip() + '\n')
        vheaders = ''.join(vheaders)
        sheaders = ';'.join(keys)

        return sheaders, '\n'.join([self.method, uri, query, vheaders,
                                    sheaders, self.bodyHash()])

    def _writeHeaders(self, transport, TEorCL):
        self._signer.signRequest(self)
        super(SigningRequest, self)._writeHeaders(transport, TEorCL)

    def _writeToChunked(self, transport):
        raise NotImplementedError('Request body signing not yet '
                                  'implemented.')

    def _writeToContentLength(self, transport):
        encoder = SigningChunkedEncoder(self.bodyProducer, transport,
                                        self._signer)

        contentLength = encoder.getChunkedLength()

        self.headers.addRawHeader('Content-Length', str(contentLength))
        self.headers.addRawHeader('Content-Encoding', 'aws-chunked')
        self.headers.addRawHeader('x-amz-decoded-content-length',
                                  str(self.bodyProducer.length))

        self._writeHeaders(transport, None)

        d = encoder.startProducing()

        def cbProduced(ignored):
            encoder.unregisterProducer()

        def ebProduced(err):
            encoder._allowNoMoreWrites()
            # Don't call the encoder's unregisterProducer because it will write
            # a zero-length chunk.  This would indicate to the server that the
            # request body is complete.  There was an error, though, so we
            # don't want to do that.
            transport.unregisterProducer()
            return err

        d.addCallbacks(cbProduced, ebProduced)
        return d


class SigningAgent(Agent):
    def __init__(self, reactor, signData, *args, **kwargs):
        super(SigningAgent, self).__init__(reactor, *args, **kwargs)
        self._signData = signData

    def _requestWithEndpoint(self, key, endpoint, method, parsedURI,
                             headers, bodyProducer, requestPath):
        if headers is None:
            headers = Headers()

        if not headers.hasHeader('host'):
            headers = headers.copy()
            headers.addRawHeader(
                'host', self._computeHostValue(parsedURI.scheme,
                                               parsedURI.host, parsedURI.port))

        d = self._pool.getConnection(key, endpoint)

        def cbConnected(proto):
            return proto.request(
                SigningRequest._construct(self._signData.makeSigner(),
                                          method, requestPath, headers,
                                          bodyProducer,
                                          persistent=self._pool.persistent,
                                          parsedURI=parsedURI))
        d.addCallback(cbConnected)
        return d
