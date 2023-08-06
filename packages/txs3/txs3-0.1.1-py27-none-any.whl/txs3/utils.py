import hashlib
import base64
import json
from pprint import pformat
from xml.etree import ElementTree as etree  # noqa
from xml.dom import minidom

from twisted.internet.protocol import Protocol
from twisted.internet import defer
from twisted.web.iweb import IBodyProducer

from zope.interface import implements


class BeginningPrinter(Protocol):
    def __init__(self, finished, maxLength=1024 * 10):
        self.finished = finished
        self.remaining = maxLength

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            print 'Some data received:'
            print display
            self.remaining -= len(display)

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.finished.callback(None)


def dumpResponse(response):
    print 'Response version:', response.version
    print 'Response code:', response.code
    print 'Response phrase:', response.phrase
    print 'Response headers:'
    print pformat(list(response.headers.getAllRawHeaders()))
    finished = defer.Deferred()
    response.deliverBody(BeginningPrinter(finished))
    finished.addCallback(lambda _: response)
    return finished


def formatXML(elem):
    reparsed = minidom.parseString(etree.tostring(elem, 'utf-8'))
    return reparsed.toprettyxml(indent='  ').strip()


class StringProducer(object):
    implements(IBodyProducer)

    contentType = 'binary/octet-stream'

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def md5Hash(self):
        return base64.b64encode(hashlib.md5(self.body).digest())

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class XMLProducer(StringProducer):

    contentType = 'application/xml'

    def __init__(self, el, encoding='utf-8'):
        super(XMLProducer, self).__init__(etree.tostring(el, encoding))


class JSONProducer(StringProducer):

    contentType = 'application/json'

    def __init__(self, obj, encoding='utf-8'):
        super(JSONProducer, self).__init__(json.dumps(obj, encoding=encoding))
