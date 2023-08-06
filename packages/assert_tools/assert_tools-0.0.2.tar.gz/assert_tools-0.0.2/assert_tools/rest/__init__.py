import httplib2
import requests
from assert_tools import assert_equal
from assert_tools.rest.response_json import responses


class UnsupportedObject(Exception):
    """The exception used by :py:method: `as_http_response` and
    dict_as_http_response."""
    pass


class UnsupportedResponseCode(Exception):
    """The exception used by :py:method: `assert_response_equal` """
    pass


def as_http_response(response, content=None):
    """
    convert request.Response object to :py:class:httplib2.Response

    :param response: a :py:class:httplib2.Response object or
                     :py:class:request.Response

    :param content: content, required for :py:class:httplib2.Response

    return: The return value is a tuple of (response, content), the first
    being and instance of the :py:class:httplib2.Response, the second being
    a string that contains the response entity body.
    """
    if isinstance(response, httplib2.Response):
        return response, content
    elif isinstance(response, requests.Response):
        r = httplib2.Response({'status': response.status_code})
        r.status = response.status_code
        return r, response.content

    raise UnsupportedObject(
        "Unsupported Object expected {0} or {1} got {2}".format(
            httplib2.Response, requests.Response, type(response))
    )


def dict_as_http_response(data_dict):
    """convert python dictionary to httplib2 'Response'

    :param data_dict: dictionary to convert to httplib2 'Response' object
        expected_keys: status and body.

    return: The return value is a tuple of (response, content), the first
    being and instance of the httplib2 'Response' class, the second being
    a string that contains the response entity body.
    """
    if isinstance(data_dict, dict):
        expected_keys = ['status', 'body']
        keys = data_dict.keys()
        if any(i in keys for i in expected_keys):
            r = httplib2.Response({'status': 200})
            r.status = data_dict.get('status', 200)
            body = data_dict.get('body', '')
            return r, body
        raise UnsupportedObject("Missing keys {0} got {1}".format(
            expected_keys, keys))
    raise UnsupportedObject("Unsupported Object expected {0} got {1}".format(
        dict, type(data_dict)))


def assert_response_equal(actual_response, expected_response):
    """Assert Response code is equal.
    :param actual_response: Actual Response
    :param expected_response: expected Response
    """
    try:
        expected_data_dict = responses[expected_response]
    except KeyError:
        raise UnsupportedResponseCode(
            'Unsupported response code, supported response codes: {0}'.format(
                responses.keys()))

    expected_response, _ = dict_as_http_response(expected_data_dict)
    actual_response, _ = as_http_response(actual_response)
    assert_equal(expected_response.status, actual_response.status)


def assert_response_headers_contains(
        actual_response, expected_content_header_dict):
    """Assert Response header contains a items in expected_header_content.
    :param actual_response: Actual Response
    :param expected_content_header_dict: expected content in response header
    """
    if not isinstance(expected_content_header_dict, dict):
        raise UnsupportedObject(
            'Python dictionary expected for expected_header_content ')
    actual_response, _ = as_http_response(actual_response)
    assert_equal(
        [i for i in expected_content_header_dict.keys() if
         i in actual_response.keys()],
        expected_content_header_dict.keys(),
        "Items not found in response header"
    )
    for i in expected_content_header_dict.keys():
        assert_equal(
            expected_content_header_dict.get(i), actual_response.get(i),
            "Unexpected header item value returned"
        )


def assert_response_content_equal(
        expected_data, actual_response_content):
    """Assert response content is equal.
    :param expected_data:expected content
    :param actual_response_content: actual content
    """
    assert_equal(expected_data, actual_response_content)


def assert_response_ok(actual_response):
    """Assert response code is OK.
    :param actual_response: actual response
    """
    assert_response_equal(actual_response, 'OK')


def assert_response_success(actual_response):
    """Assert response code is SUCCESS.
    :param actual_response: actual response
    """
    assert_response_equal(actual_response, 'SUCCESS')


def assert_response_not_allowed(actual_response):
    """Assert response code is NOT_ALLOWED.
    :param actual_response: actual response
    """
    assert_response_equal(actual_response, 'NOT_ALLOWED')


def assert_response_forbidden(actual_response):
    """Assert response code is FORBIDDEN.
    :param actual_response: actual response
    """
    assert_response_equal(actual_response, 'FORBIDDEN')


def assert_response_deny(actual_response):
    """Assert response code is DENY.
    :param actual_response: actual response
    """
    assert_response_equal(actual_response, 'DENY')


def assert_response_bad_request(actual_response):
    """Assert response code is BAD_REQUEST.
    :param actual_response: actual response
    """
    assert_response_equal(actual_response, 'BAD_REQUEST')


def make_api_call(url, method, kwargs):
    """
    Perform the call allowed  by httplib2 ``method``
    :param url: Rest API url

    :param method: :py:class:httplib.HTTP request method: GET, POST, PUT,
        DELETE
    :param kwargs: dictionary of supported :py:class:httplib2.Http() request
         body, headers, redirections, connection_type

    return: The return value is a tuple of (response, content), the first
            being and instance of the httplib2 'Response' class, the second
            being a string that contains the response entity body.

    usage: extra_args = {
           'body': {'abc': 123},
           'headers'={},
           'redirections':3,
           'connection_type':'http'}
           make_api_call('some_http_url', 'PUT', extra_args)
    """
    client = httplib2.Http()
    return client.request(url, method=method, **kwargs)


def assert_get_request_returns_ok_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert get request returns okay status code
     * Perform GET request to sever url
     * Assert response is OK
     * Assert response content is matches the expected content

    :param server_url:
    :param expected_content:
    :param request_kwargs:
    """
    response, actual_content = make_api_call(server_url, 'GET', request_kwargs)
    assert_response_ok(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_get_request_returns_success_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert get request returns okay status code
     * Perform GET request to sever url
     * Assert response is SUCCESS
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'GET', request_kwargs)
    assert_response_success(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_get_request_returns_not_allowed_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert get request returns okay status code
     * Perform GET request to sever url
     * Assert response is NOT_ALLOWED
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'GET', request_kwargs)
    assert_response_not_allowed(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_get_request_returns_forbidden_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert get request returns okay status code
     * Perform GET request to sever url
     * Assert response is FORBIDDEN
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'GET', request_kwargs)
    assert_response_forbidden(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_get_request_returns_deny_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert get request returns okay status code
     * Perform GET request to sever url
     * Assert response is DENY
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'GET', request_kwargs)
    assert_response_deny(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_get_request_returns_bad_request_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert get request returns okay status code
    * Perform GET request to sever url
    * Assert response is DENY
    * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'GET', request_kwargs)
    assert_response_bad_request(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_post_request_returns_ok_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert post request returns okay status code
     * Perform POST request to sever url
     * Assert response is POST
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'POST',
                                             request_kwargs)
    assert_response_ok(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_post_request_returns_success_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert post request returns okay status code
     * Perform POST request to sever url
     * Assert response is SUCCESS
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'POST',
                                             request_kwargs)
    assert_response_success(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_post_request_returns_not_allowed_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert post request returns okay status code
     * Perform POST request to sever url
     * Assert response is NOT_ALLOWED
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'POST',
                                             request_kwargs)
    assert_response_not_allowed(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_post_request_returns_forbidden_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert post request returns okay status code
     * Perform POST request to sever url
     * Assert response is FORBIDDEN
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'POST',
                                             request_kwargs)
    assert_response_forbidden(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_post_request_returns_deny_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert post request returns okay status code
     * Perform POST request to sever url
     * Assert response is DENY
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'GET', request_kwargs)
    assert_response_deny(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_post_request_returns_bad_request_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert get request returns okay status code
     * Perform POST request to sever url
     * Assert response is DENY
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'POST',
                                             request_kwargs)
    assert_response_bad_request(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_put_request_returns_ok_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert put request returns okay status code
     * Perform PUT request to sever url
     * Assert response is OK
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'PUT',
                                             request_kwargs)
    assert_response_ok(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_put_request_returns_success_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert put request returns okay status code
     * Perform PUT request to sever url
     * Assert response is SUCCESS
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'PUT',
                                             request_kwargs)
    assert_response_success(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_put_request_returns_not_allowed_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert put request returns okay status code
     * Perform PUT request to sever url
     * Assert response is NOT_ALLOWED
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'PUT',
                                             request_kwargs)
    assert_response_not_allowed(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_put_request_returns_forbidden_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert put request returns okay status code
     * Perform PUT request to sever url
     * Assert response is FORBIDDEN
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'PUT',
                                             request_kwargs)
    assert_response_forbidden(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_put_request_returns_deny_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert put request returns okay status code
     * Perform PUT request to sever url
     * Assert response is DENY
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'PUT',
                                             request_kwargs)
    assert_response_deny(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_put_request_returns_bad_request_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert put request returns okay status code
     * Perform PUT request to sever url
     * Assert response is DENY
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'PUT',
                                             request_kwargs)
    assert_response_bad_request(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_delete_request_returns_ok_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert delete request returns okay status code
     * Perform DELETE request to sever url
     * Assert response is OK
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'DELETE',
                                             request_kwargs)
    assert_response_ok(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_delete_request_returns_success_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert delete request returns okay status code
     * Perform DELETE request to sever url
     * Assert response is SUCCESS
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'DELETE',
                                             request_kwargs)
    assert_response_success(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_delete_request_returns_not_allowed_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert delete request returns okay status code
     * Perform GET request to sever url
     * Assert response is NOT_ALLOWED
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'DELETE',
                                             request_kwargs)
    assert_response_not_allowed(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_delete_request_returns_forbidden_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert delete request returns okay status code
     * Perform DELETE request to sever url
     * Assert response is FORBIDDEN
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'DELETE',
                                             request_kwargs)
    assert_response_forbidden(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_delete_request_returns_deny_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert delete request returns okay status code
     * Perform DELETE request to sever url
     * Assert response is DENY
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'DELETE',
                                             request_kwargs)
    assert_response_deny(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_delete_request_returns_bad_request_status_code(
        server_url, expected_content=None, request_kwargs=None):
    """
    Assert delete request returns okay status code
     * Perform DELETE request to sever url
     * Assert response is DENY
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'DELETE',
                                             request_kwargs)
    assert_response_bad_request(response)
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)


def assert_options_request_returns_ok_status_code(
        server_url, expected_content_header_dict=None,
        expected_content=None, request_kwargs=None):
    """
    Assert options request returns okay status code
     * Perform OPTIONS request to sever url
     * Assert response is OK
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content: expected content in content
        returned :py:class:httplib.HTTP request
    :param expected_content_header_dict: python dict containing expected
        key value pairing in response returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'OPTIONS',
                                             request_kwargs)
    assert_response_ok(response)
    if expected_content_header_dict:
        assert_response_headers_contains(
            response, expected_content_header_dict
        )
    if expected_content:
        assert_response_content_equal(expected_content, actual_content)
    if expected_content_header_dict:
        assert_response_headers_contains(
            response, expected_content_header_dict
        )


def assert_head_request_returns_ok_status_code(
        server_url, expected_content_header_dict=None, request_kwargs=None):
    """
    Assert options request returns okay status code
     * Perform HEAD request to sever url
     * Assert response is OK
     * Assert response content is matches the expected content

    :param server_url: server url
    :param expected_content_header_dict: python dict containing expected
        key value pairing in response returned :py:class:httplib.HTTP request
    :param request_kwargs: keyword arguments for :py:class:httplib.HTTP
        request
    """
    response, actual_content = make_api_call(server_url, 'HEAD',
                                             request_kwargs)
    assert_response_ok(response)
    if expected_content_header_dict:
        assert_response_headers_contains(
            response, expected_content_header_dict
        )
    if expected_content_header_dict:
        assert_response_headers_contains(
            response, expected_content_header_dict
        )

del response_json
