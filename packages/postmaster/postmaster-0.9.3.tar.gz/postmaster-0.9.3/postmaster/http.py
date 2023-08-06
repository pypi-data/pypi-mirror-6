import urllib, os
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise
from .conf import config

__all__ = [
    'PostmasterError',
    'APIError',
    'NetworkError',
    'AuthenticationError',
    'PermissionError',
    'InvalidDataError',
    'HTTPTransport'
]

HTTP_LIB = None

# Try to import the appropriate HTTP library
# for the current system.
try:
    from google.appengine.api import urlfetch
    if not 'CURRENT_VERSION_ID' in os.environ:
        raise ImportError
    HTTP_LIB = 'urlfetch'
except ImportError:
    try:
        import pycurl
        HTTP_LIB = 'pycurl'
    except ImportError:
        try:
            import urllib2
            HTTP_LIB = 'urllib2'
        except ImportError:
            raise

class PostmasterError(Exception):
    def __init__(self, message=None, http_body=None, http_status=None, json_body=None):
        super(PostmasterError, self).__init__(message)
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body


class APIError(PostmasterError):
    """
    An error with the Postmaster API, 500 or similar.
    """
    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return 'API Error: %s' % (self.http_body)


class NetworkError(PostmasterError):
    """
    An error with your network connectivity.
    """
    pass

class AuthenticationError(PostmasterError):
    """
    401 style error
    """
    pass


class PermissionError(PostmasterError):
    """
    403 style error.
    """
    pass


class InvalidDataError(PostmasterError):
    """
    400 style error.
    """
    pass


class HTTPTransport(object):

    @classmethod
    def _decode(cls, response_data, response_code):
        if response_code >= 500:
            raise APIError("There was an API error.", http_body=response_data)

        try:
            data = json.loads(response_data)
            if response_code > 299:
                data = data['message']
        except (ValueError, KeyError):
            data = response_data

        if response_code == 400:
            raise InvalidDataError(data, json_body=response_data)
        elif response_code == 401:
            raise AuthenticationError(data, json_body=response_data)
        elif response_code == 403:
            raise PermissionError(data, json_body=response_data)

        return data

    @classmethod
    def post(cls, url, data=None, headers=None):
        # Pass data in already encoded, valid data is returned as a dict
        headers = headers if headers else {}
        headers.update(config.headers)
        if HTTP_LIB == 'urlfetch':
            try:
                if data:
                    data = json.dumps(data)
                url = '%s%s' % (config.base_url, url)
                resp = urlfetch.fetch(url, data, method='POST', headers=headers, deadline=30)
            except urlfetch.DownloadError:
                raise NetworkError("There was a network error.")
            else:
                return cls._decode(resp.content, resp.status_code)

        elif HTTP_LIB == 'pycurl':
            import StringIO
            buf = StringIO.StringIO()
            try:
                c = pycurl.Curl()
                c.setopt(pycurl.CONNECTTIMEOUT, 30)
                c.setopt(pycurl.TIMEOUT, 30)
                c.setopt(pycurl.WRITEFUNCTION, buf.write)
                c.setopt(pycurl.POST, 1)
                if data:
                    data = json.dumps(data)
                c.setopt(pycurl.POSTFIELDS, data or '')
                url = '%s%s' % (config.base_url, url)
                c.setopt(c.URL, url)

                if headers:
                    c.setopt(c.HTTPHEADER, ['%s: %s' % (k,v) for k,v in headers.iteritems()])
                c.setopt(c.FAILONERROR, False)
                c.perform()
                status_code = c.getinfo(pycurl.HTTP_CODE)
                c.close()
            except pycurl.error, error:
                errno, errstr = error
            else:
                return cls._decode(buf.getvalue(), status_code)
        elif HTTP_LIB == 'urllib2':
            try:
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                if data:
                    data = json.dumps(data)

                request = urllib2.Request('%s%s' % (config.base_url, url), data=data, headers=headers)
                request.get_method = lambda: 'POST'
                resp = opener.open(request, timeout=30)
                return cls._decode(resp.read(), resp.getcode())
            except urllib2.HTTPError, e:
                return cls._decode(e.read(), e.getcode())

    @classmethod
    def get(cls, url, data=None, headers=None):
        headers = headers if headers else {}
        headers.update(config.headers)

        if HTTP_LIB == 'urlfetch':
            try:
                url = '%s%s' % (config.base_url, url)
                if data:
                    data = urllib.urlencode(data)
                    url += ('?%s' % data)

                resp = urlfetch.fetch(url, method='GET', headers=headers, deadline=30)
            except urlfetch.DownloadError:
                raise NetworkError("There was a network error.")
            else:
                return cls._decode(resp.content, resp.status_code)
        elif HTTP_LIB == 'pycurl':
            import StringIO
            buf = StringIO.StringIO()
            try:
                c = pycurl.Curl()
                c.setopt(pycurl.CONNECTTIMEOUT, 30)
                c.setopt(pycurl.TIMEOUT, 30)
                c.setopt(pycurl.WRITEFUNCTION, buf.write)
                url = '%s%s' % (config.base_url, url)
                if data:
                    data = urllib.urlencode(data)
                    url += ('?%s' % data)
                c.setopt(c.URL, url)
                if headers:
                    c.setopt(c.HTTPHEADER, ['%s: %s' % (k,v) for k,v in headers.iteritems()])
                c.setopt(c.FAILONERROR, False)
                c.perform()
                status_code = c.getinfo(pycurl.HTTP_CODE)
                c.close()
            except pycurl.error, error:
                errno, errstr = error
            else:
                return cls._decode(buf.getvalue(), status_code)
        elif HTTP_LIB == 'urllib2':
            try:
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                headers['Accept'] = 'application/json'
                url = '%s%s' % (config.base_url, url)
                if data:
                    data = urllib.urlencode(data)
                    url += ('?%s' % data)
                request = urllib2.Request(url, headers=headers)
                request.get_method = lambda: 'GET'
                resp = opener.open(request, timeout=30)
                return cls._decode(resp.read(), resp.getcode())
            except urllib2.HTTPError, e:
                return cls._decode(e.read(), e.getcode())

    @classmethod
    def put(cls, url, data=None, headers=None):
        headers = headers if headers else {}
        headers.update(config.headers)
        if HTTP_LIB == 'urlfetch':
            try:
                if data:
                    data = json.dumps(data)
                url = '%s%s' % (config.base_url, url)
                resp = urlfetch.fetch(url, data, method='PUT', headers=headers, deadline=30)
            except urlfetch.DownloadError:
                raise NetworkError("There was a network error.")
            else:
                return cls._decode(resp.content, resp.status_code)
        elif HTTP_LIB == 'pycurl':
            import StringIO
            buf = StringIO.StringIO()
            try:
                c = pycurl.Curl()
                c.setopt(pycurl.CONNECTTIMEOUT, 30)
                c.setopt(pycurl.TIMEOUT, 30)
                c.setopt(pycurl.WRITEFUNCTION, buf.write)
                c.setopt(pycurl.PUT, 1)

                if data:
                    data = json.dumps(data)
                    data_io = StringIO.StringIO(data)
                    content_length = len(data)
                    c.setopt(pycurl.READFUNCTION, data_io.read)
                    c.setopt(pycurl.INFILESIZE, content_length)
                else:
                    c.setopt(pycurl.INFILESIZE, 0)

                url = '%s%s' % (config.base_url, url)
                c.setopt(c.URL, url)
                if headers:
                    c.setopt(c.HTTPHEADER, ['%s: %s' % (k,v) for k,v in headers.iteritems()])
                c.setopt(c.FAILONERROR, False)
                c.perform()
                status_code = c.getinfo(pycurl.HTTP_CODE)
                c.close()
            except pycurl.error, error:
                errno, errstr = error
            else:
                return cls._decode(buf.getvalue(), status_code)
        elif HTTP_LIB == 'urllib2':
            try:
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                if data:
                    data = json.dumps(data)

                request = urllib2.Request('%s%s' % (config.base_url, url), data=data, headers=headers)
                request.get_method = lambda: 'PUT'
                resp = opener.open(request, timeout=30)
                return cls._decode(resp.read(), resp.getcode())
            except urllib2.HTTPError, e:
                return cls._decode(e.read(), e.getcode())

    @classmethod
    def delete(cls, url, data=None, headers=None):
        headers = headers if headers else {}
        headers.update(config.headers)
        if HTTP_LIB == 'urlfetch':
            try:
                if data:
                    data = json.dumps(data)
                    raise NotImplementedError
                ## urlfetch doesn't allow you to send body when performing DELETE request
                ## issue : http://code.google.com/p/googleappengine/issues/detail?id=601
                url = '%s%s' % (config.base_url, url)
                resp = urlfetch.fetch(url, data, method='DELETE', headers=headers, deadline=30)
            except urlfetch.DownloadError:
                raise NetworkError("There was a network error.")
            else:
                return cls._decode(resp.content, resp.status_code)
        elif HTTP_LIB == 'pycurl':
            import StringIO
            buf = StringIO.StringIO()
            try:
                c = pycurl.Curl()
                c.setopt(pycurl.CONNECTTIMEOUT, 30)
                c.setopt(pycurl.TIMEOUT, 30)
                c.setopt(pycurl.WRITEFUNCTION, buf.write)
                c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
                if data:
                    raise NotImplementedError
                else:
                    c.setopt(pycurl.INFILESIZE, 0)
                url = '%s%s' % (config.base_url, url)
                c.setopt(c.URL, url)
                if headers:
                    c.setopt(c.HTTPHEADER, ['%s: %s' % (k,v) for k,v in headers.iteritems()])
                c.setopt(c.FAILONERROR, False)
                c.perform()
                status_code = c.getinfo(pycurl.HTTP_CODE)
                c.close()
            except pycurl.error, error:
                errno, errstr = error
            else:
                return cls._decode(buf.getvalue(), status_code)
        elif HTTP_LIB == 'urllib2':
            try:
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                if data:
                    data = json.dumps(data)

                request = urllib2.Request('%s%s' % (config.base_url, url), data=data, headers=headers)
                request.get_method = lambda: 'DELETE'
                resp = opener.open(request, timeout=30)
                return cls._decode(resp.read(), resp.getcode())
            except urllib2.HTTPError, e:
                return cls._decode(e.read(), e.getcode())
