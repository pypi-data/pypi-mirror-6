from assert_tools import assert_equal, assert_raises

from assert_tools.rest import (
    UnsupportedObject,
    dict_as_http_response)
from util import MockHttpResponse


def test_dict_as_http_response():
    """
    Tests :py:func:`assert_tools.rest.dict_as_http_response`.

    Tests that :py:func:`assert_tools.rest.dict_as_http_response`
    returns :py:class:requests.Response object when given a conforming python
    dict
    """
    mock_http_response = MockHttpResponse()
    data_dict = {'status': 200, 'body': {234: 'bcd'}}
    result = dict_as_http_response(data_dict)
    assert_equal(mock_http_response(**data_dict), result)


def test_dict_as_http_response_malformed_dict():
    """
    Tests :py:func:`assert_tools.rest.dict_as_http_response`.

    Tests that :py:func:`assert_tools.rest.dict_as_http_response`
    raises :py:class:`assert_tools.rest.UnsupportedObject`
    when give a non-conforming dict
    """
    data_dict = {'bar': 200, 'foo': {234: 'bcd'}}
    assert_raises(UnsupportedObject, dict_as_http_response, data_dict)


def test_dict_as_http_response_not_dict():
    """
    Tests :py:func:`assert_tools.rest.dict_as_http_response`.

    Tests that :py:func:`assert_tools.rest.dict_as_http_response`
    raises :py:class:`assert_tools.rest.UnsupportedObject`
    when give a non-dict structure
    """

    not_dict = [4356789]
    assert_raises(UnsupportedObject, dict_as_http_response, not_dict)