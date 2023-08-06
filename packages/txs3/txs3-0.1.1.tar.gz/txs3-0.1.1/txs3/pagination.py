from twisted.internet import defer

from .client import ns


class PaginatedResultsGetter(object):
    def __init__(self, pageGetter, marker=None, limit=100):
        self._getter = pageGetter
        self._marker = marker
        self._limit = limit
        self._done = False
        self._lock = defer.DeferredLock()

    @defer.inlineCallbacks
    def getNextPage(self):
        yield self._lock.acquire()
        try:
            assert not self._done, 'Last page already requested'
            page = yield self._getter(marker=self._marker, limit=self._limit)
            if self.getTruncated(page):
                self._marker = self.getNextMarker(page)
                self._done = False
            else:
                self._done = True
            defer.returnValue((page, self._done))
        finally:
            self._lock.release()

    def getTruncated(self, page):
        return page.findtext(ns('IsTruncated')) == 'true'

    def getNextMarker(self, page):
        marker = page.findtext(ns('NextMarker'))
        if not marker:
            lastElement = page.findall(ns('Contents'))[-1]
            marker = lastElement.findtext(ns('Key'))
        return marker


class PageFlatteningDeferredIterator(object):
    def __init__(self, pageResultsGetter):
        self._getter = pageResultsGetter
        self._done = False
        self._objects = []
        self._lock = defer.DeferredLock()

    def _getResults(self, page):
        common = page.findall(ns('CommonPrefixes'))
        contents = page.findall(ns('Contents'))
        return common + contents

    def _gotPage(self, (page, isLast)):
        results = self._getResults(page)
        if not results:
            raise StopIteration()
        current = results[0]

        self._objects = results[1:]
        self._done = isLast

        return current

    @defer.inlineCallbacks
    def asList(self):
        results = []
        while True:
            page, isLast = yield self._getter.getNextPage()
            results += self._getResults(page)
            if isLast:
                break
        defer.returnValue(results)

    @defer.inlineCallbacks
    def consume(self, func):
        for d in self:
            result = yield d
            yield defer.maybeDeferred(func, result)

    def _nextResult(self):
        if self._objects:
            d = defer.succeed(self._objects.pop(0))
        else:
            if self._done:
                return None
            d = self._getter.getNextPage()
            d.addCallback(self._gotPage)
        return d

    def __iter__(self):
        while True:
            r = self._nextResult()
            if not r:
                break
            yield r
