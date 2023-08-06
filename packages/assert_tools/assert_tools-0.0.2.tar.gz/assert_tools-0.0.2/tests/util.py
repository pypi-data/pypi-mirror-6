import httplib2
import requests


class MockHttpResponse():
    def __call__(self, status=200, body=None):
        if not body:
            body = {123: 'abc'}
        r = httplib2.Response({'status': status})
        return r, body


class MockRequestsResponse():
    def __call__(self):
        r = requests.Response()
        r.status_code = 200
        r._content = {123: 'abc'}
        return r
