import xml.etree.ElementTree as etree
from collections import namedtuple

from twisted.internet import defer

from . import client, utils, error, pagination
from .client import ns


__all__ = ['Service', 'Bucket', 'Object']


def simpleOperation(action='', method='GET'):
    def func(self):
        return self._request(method, action)
    return func


def versionedOperation(action='', method='GET'):
    def func(self, versionId=None):
        params = {'versionId': versionId} if versionId else None
        return self._request(method, action, params=params)
    return func


def simpleBodyOperation(action='', method='PUT',
                        producerClass=utils.XMLProducer):
    def func(self, body):
        body = producerClass(body)
        return self._request(method, action, body=body)
    return func


def callbackOperation(action='', method='GET'):
    def wrapper(callback):
        def wrapped(self):
            d = self._request(method, action)
            d.addCallback(lambda xml: callback(self, xml))
            return d
        return wrapped
    return wrapper


class Service(client.S3Client):
    def __init__(self, client):
        self._client = client

    def _request(self, *args, **kwargs):
        return self._client.makeRequest(None, None, *args, **kwargs)

    def bucket(self, bucketName):
        return Bucket(self, bucketName)

    @callbackOperation()
    def buckets(self, bucketsXML):
        buckets = bucketsXML.iterfind(ns('Buckets', 'Bucket', 'Name'))
        return [Bucket(self, b.text) for b in buckets]


class Bucket(object):
    cannedACLs = [
        'private',
        'public-read',
        'public-read-write',
        'authenticated-read',
        'bucket-owner-read',
        'bucket-owner-full-control',
    ]

    payers = [
        'Requester',
        'BucketOwner',
    ]

    def __init__(self, service, name):
        self._client = service._client
        self.name = name

    def __repr__(self):
        return 'Bucket({!r})'.format(self.name)

    def _request(self, *args, **kwargs):
        return self._client.makeRequest(self.name, None, *args, **kwargs)

    def object(self, key):
        return Object(self, key)

    def objects(self, prefix=None, delimiter=None, marker=None, limit=1000):
        def pageGetter(marker, limit):
            return self._request('GET', params={
                'prefix': prefix,
                'delimiter': delimiter,
                'marker': marker,
                'max-keys': limit,
            })

        pages = pagination.PaginatedResultsGetter(pageGetter, marker, limit)
        return pagination.PageFlatteningDeferredIterator(pages)

    def exists(self):
        def cbResponse(response):
            if response.code not in (200, 301, 403, 404):
                return self._client.processResponse(response)
            return response.code != 404

        d = self._request('HEAD', processResponse=False)
        d.addCallback(cbResponse)
        return d

    def accessible(self):
        def cbResponse(response):
            if response.code not in (200, 301, 403, 404):
                return self._client.processResponse(response)
            return response.code == 200

        d = self._request('HEAD', processResponse=False)
        d.addCallback(cbResponse)
        return d

    acl = simpleOperation('acl')
    setAcl = simpleBodyOperation('acl')

    cors = simpleOperation('cors')
    setCors = simpleBodyOperation('cors')
    deleteCors = simpleOperation('cors', method='DELETE')

    lifecycle = simpleOperation('lifecycle')
    setLifecycle = simpleBodyOperation('lifecycle')
    deleteLifecycle = simpleOperation('lifecycle', method='DELETE')

    policy = simpleOperation('policy')
    # TODO: This currently raises an IncompleteBody error, but the sent bytes
    # appear to be correct.
    setPolicy = simpleBodyOperation('policy', producerClass=utils.JSONProducer)
    deletePolicy = simpleOperation('policy', method='DELETE')

    def versions(self):
        raise NotImplementedError('Object versions listing not implemented.')

    def multipartUploads(self):
        raise NotImplementedError('Multipart uploads listing not implemented.')

    @callbackOperation('location')
    def location(self, locationXML):
        return locationXML.text

    logging = simpleOperation('logging')
    setLogging = simpleBodyOperation('logging')

    notification = simpleOperation('notification')
    setNotification = simpleBodyOperation('notification')

    tagging = simpleOperation('tagging')
    setTagging = simpleBodyOperation('tagging')
    deleteTagging = simpleOperation('tagging', method='DELETE')

    @callbackOperation('requestPayment')
    def requestPayment(self, paymentXML):
        return paymentXML.findtext(ns('Payer'))

    def setRequestPayment(self, payer):
        """
        TODO: This currently raises MalformedXML, but the XML snippet is taken
        directly from the documentation.
        """
        assert payer in self.payers, 'Invalid payer provided: {}'.format(payer)

        config = etree.Element(ns('RequestPaymentConfiguration'))
        payerElement = etree.SubElement(config, ns('Payer'))
        payerElement.text = payer

        body = utils.XMLProducer(config)

        return self._request('PUT', body=body)

    def versioning(self):
        def cbResponse(versioningXML):
            return versioningXML.findtext(ns('Status'))

        d = self._request('GET', 'versioning',
                          responseContentType='application/xml')
        d.addCallback(cbResponse)
        return d

    def enableVersioning(self):
        """
        TODO: This currently raises MalformedXML, but the XML snippet is taken
        directly from the documentation.
        """
        config = etree.Element(ns('VersioningConfiguration'))
        status = etree.SubElement(config, ns('Status'))
        status.text = 'Enabled'

        body = utils.XMLProducer(config)

        return self._request('PUT', body=body)

    def suspendVersioning(self):
        """
        TODO: This currently raises MalformedXML, but the XML snippet is taken
        directly from the documentation.
        """
        config = etree.Element(ns('VersioningConfiguration'))
        status = etree.SubElement(config, ns('Status'))
        status.text = 'Suspended'

        body = utils.XMLProducer(config)

        return self._request('PUT', body=body)

    website = simpleOperation('website')
    setWebsite = simpleBodyOperation('website')
    deleteWebsite = simpleOperation('website', method='DELETE')

    def create(self, acl='private'):
        """
        TODO: Support explicit permissions by providing a dictionary as value
        for the acl parameter.
        """
        assert acl in self.cannedACLs, 'Invalid ACL provided: {}'.format(acl)

        config = etree.Element(ns('CreateBucketConfiguration'))
        location = etree.SubElement(config, ns('LocationConstraint'))
        location.text = self._client._region

        def ebExisting(failure):
            failure.trap(error.BucketAlreadyOwnedByYou)
            return False

        body = utils.XMLProducer(config)

        d = self._request('PUT', body=body, headers={
            'x-amz-acl': acl,
        })
        d.addCallbacks(lambda _: True, ebExisting)
        return d

    delete = simpleOperation(method='DELETE')

    def deleteObjects(self, objects):
        # TODO: Better error reporting
        spec = etree.Element(ns('Delete'))
        quiet = etree.SubElement(spec, ns('Quiet'))
        quiet.text = 'true'

        for o in objects:
            obj = etree.SubElement(spec, ns('Object'))
            key = etree.SubElement(obj, ns('Key'))
            if isinstance(o, basestring):
                key.text = o
            else:
                key.text = o[0]
                vid = etree.SubElement(obj, ns('VersionId'))
                vid.text = o[1]

        body = utils.XMLProducer(spec)
        return self._request('POST', action='delete', body=body)


class Object(object):
    """
    TODO: implement the following operations

    * HEAD Object
    * POST Object restore
    * PUT Object - Copy
    * Initiate Multipart Upload
    * Upload Part
    * Upload Part - Copy
    * Complete Multipart Upload
    * Abort Multipart Upload
    * List Parts
    """

    def __init__(self, bucket, key):
        self._client = bucket._client
        self._bucket = bucket
        self.key = key

    def _request(self, *args, **kwargs):
        return self._client.makeRequest(self._bucket.name, self.key,
                                        *args, **kwargs)

    def get(self, versionId=None):
        # TODO: Implement all the additional features supported by AWS, such as
        # versioning, range, if-* headers. Respone headers overwriting is not
        # needed here
        params = {'versionId': versionId} if versionId else None
        return self._request('GET', params=params, processResponse=False)

    def upload(self, contentsProducer):
        # TODO: Implement the following
        # expires
        # cache-control
        # content-disposition
        # contentType (overwrite the one provided by the producer)
        # encryption
        # acl
        # meta=None
        # storageClass=None
        # redirect=None

        def cbProcessed(response, version):
            return version if response is None else response

        def cbResponse(response):
            version = response.headers.getRawHeaders(
                'x-amz-version-id', [None])[0]
            d = defer.maybeDeferred(self._client.processResponse, response)
            d.addCallback(cbProcessed, version)
            return d

        d = self._request('PUT', body=contentsProducer, processResponse=False)
        d.addCallback(cbResponse)
        return d

    def delete(self, versionId=None):
        def cbProcessed(response, version, marker):
            if version == 'null':
                version = None

            if versionId:
                assert versionId == version
                r = DeletionResult(
                    marker=None,
                    deleted=(marker == 'true'),
                )
            else:
                r = DeletionResult(
                    marker=version,
                    deleted=False,
                )

            return r if response is None else response

        def cbResponse(response):
            version = response.headers.getRawHeaders(
                'x-amz-version-id', [None])[0]
            marker = response.headers.getRawHeaders(
                'x-amz-delete-marker', [None])[0]
            d = defer.maybeDeferred(self._client.processResponse, response)
            d.addCallback(cbProcessed, version, marker)
            return d

        params = {'versionId': versionId} if versionId else None
        d = self._request('DELETE', params=params, processResponse=False)
        d.addCallback(cbResponse)
        return d

    acl = versionedOperation('acl')
    setAcl = simpleBodyOperation('acl')

    torrent = simpleOperation('torrent')

DeletionResult = namedtuple('DeletionResult', ['marker', 'deleted'])
