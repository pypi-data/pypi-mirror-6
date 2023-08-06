import warnings


class S3Error(Exception):
    pass


class S3ResponseError(S3Error):
    def __init__(self, xml):
        super(S3ResponseError, self).__init__(xml.findtext('Message'))
        self._xml = xml

        self.code = xml.findtext('Code')
        self.requestId = xml.findtext('RequestId')
        self.hostId = xml.findtext('HostId')
        self.resource = xml.findtext('Resource')

    @classmethod
    def raiseFromXML(cls, xml):
        exceptionName = xml.findtext('Code')
        exceptionClass = globals().get(exceptionName, None)
        if not exceptionClass:
            warnings.warn('Dynamically generating exception class for error '
                          '{}'.format(exceptionName), RuntimeWarning)
            exceptionClass = type(exceptionName, (cls,), {})
        else:
            assert issubclass(exceptionClass, cls)
        raise exceptionClass(xml)

# TODO: Add remaining error classes.


class AccessDenied(S3ResponseError):
    pass


class MalformedXML(S3ResponseError):
    pass


class NoSuchTagSet(S3ResponseError):
    pass


class NoSuchWebsiteConfiguration(S3ResponseError):
    pass


class BucketAlreadyOwnedByYou(S3ResponseError):
    pass


class IncompleteBody(S3ResponseError):
    pass


class SignatureDoesNotMatch(S3ResponseError):
    def __init__(self, xml):
        super(SignatureDoesNotMatch, self).__init__(xml)

        self.canonicalRequest = xml.findtext('CanonicalRequest')
        self.stringToSign = xml.findtext('StringToSign')
