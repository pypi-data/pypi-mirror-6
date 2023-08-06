from assert_tools import assert_equal, assert_raises
from assert_tools.rest import (
    as_http_response,
    UnsupportedObject
)
from util import MockHttpResponse, MockRequestsResponse


def test_as_http_response_support_for_httplib_response():
    """
    Tests :py:func:`assert_tools.rest.as_http_response`.

    Tests that :py:func:`assert_tools.rest.as_http_response`
    returns :py:class:httplib.Response  object
    when given :py:class:httplib.Response
    """
    mock_http_response = MockHttpResponse()
    result = as_http_response(*mock_http_response())
    assert_equal(mock_http_response(), result)


def test_as_http_response_support_for_requests_response():
    """
    Tests :py:func:`assert_tools.rest.as_http_response`.

    Tests that :py:func:`assert_tools.rest.as_http_response`
    returns :py:class:httplib.Response object
    when given :py:class:requests.Response
    """
    mock_requests_response = MockRequestsResponse()
    mock_http_response = MockHttpResponse()
    result = as_http_response(mock_requests_response())
    assert_equal(mock_http_response(), result)


def test_as_http_response_invalid_object():
    """
    Tests :py:func:`assert_tools.rest.as_http_response`.

    Tests that :py:func:`assert_tools.rest.as_http_response`
    raises :py:class `assert_tools.rest.UnsupportedObject`` when
    given an unsupported value
    """
    assert_raises(UnsupportedObject, as_http_response, 'foo')
