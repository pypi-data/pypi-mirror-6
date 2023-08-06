from mock import patch, MagicMock

from assert_tools import rest
from assert_tools.rest.response_json import responses
from util import MockHttpResponse


_find_funcs = lambda function_matcher, module: [
    getattr(module, func) for func in dir(module) if func.startswith(
        function_matcher)]


def _look_up(code, func_list):
    for func in func_list:
        if code.lower() in func.func_name:
            return func


def test_assert_get_request_returns_status_codes():
    """
    Functional tests for
    :py:func:`assert_tools.rest.assert_get_request_returns_ok_status_code`
    :py:func:`assert_tools.rest.assert_get_request_returns_success_status_code`
    :py:func:`assert_tools.rest.assert_get_request_returns_not_allowed_status_code`
    :py:func:`assert_tools.rest.assert_get_request_returns_forbidden_status_code`.
    :py:func:`assert_tools.rest.assert_get_request_returns_deny_status_code`.
    :py:func:`assert_tools.rest.assert_get_request_returns_bad_request_status_code`.
    """
    assertions = _find_funcs('assert_get_request', rest)
    for k, v in responses.items():
        mock_http_response = MockHttpResponse()
        assertion = _look_up(k, assertions)
        with patch('assert_tools.rest.make_api_call',
                   MagicMock(return_value=mock_http_response(**v))):
            yield assertion, 'http://test.url', v["body"], {}


def test_assert_post_request_returns_status_codes():
    """
    Functional tests for
    :py:func:`assert_tools.rest.assert_post_request_returns_ok_status_code`
    :py:func:`assert_tools.rest.assert_post_request_returns_not_allowed_status_code`
    :py:func:`assert_tools.rest.assert_post_request_returns_forbidden_status_code`
    :py:func:`assert_tools.rest.assert_post_request_returns_deny_status_code`
    :py:func:`assert_tools.rest.assert_post_request_returns_bad_request_status_code`
    """
    assertions = _find_funcs('assert_post_request', rest)
    for k, v in responses.items():
        mock_http_response = MockHttpResponse()
        assertion = _look_up(k, assertions)
        with patch('assert_tools.rest.make_api_call',
                   MagicMock(return_value=mock_http_response(**v))):
            yield assertion, 'http://test.url', v["body"], {}


def test_assert_put_request_returns_status_codes():
    """
    Functional tests for
    :py:func:`assert_tools.rest.assert_put_request_returns_ok_status_code`
    :py:func:`assert_tools.rest.assert_put_request_returns_success_status_code`
    :py:func:`assert_tools.rest.assert_put_request_returns_not_allowed_status_code`
    :py:func:`assert_tools.rest.assert_put_request_returns_forbidden_status_code`
    :py:func:`assert_tools.rest.assert_put_request_returns_deny_status_code`
    :py:func:`assert_tools.rest.assert_put_request_returns_bad_request_status_code`
    """
    assertions = _find_funcs('assert_put_request', rest)
    for k, v in responses.items():
        mock_http_response = MockHttpResponse()
        assertion = _look_up(k, assertions)
        with patch('assert_tools.rest.make_api_call',
                   MagicMock(return_value=mock_http_response(**v))):
            yield assertion, 'http://test.url', v["body"], {}


def test_assert_delete_request_returns_status_codes():
    """
    Functional tests for
    :py:func:`assert_tools.rest.assert_delete_request_returns_ok_status_code`
    :py:func:`assert_tools.rest.assert_delete_request_returns_success_status_code`
    :py:func:`assert_tools.rest.assert_delete_request_returns_not_allowed_status_code`
    :py:func:`assert_tools.rest.assert_delete_request_returns_forbidden_status_code`
    :py:func:`assert_tools.rest.assert_delete_request_returns_deny_status_code`
    :py:func:`assert_tools.rest.assert_delete_request_returns_bad_request_status_code`
    """
    assertions = _find_funcs('assert_delete_request', rest)
    for k, v in responses.items():
        mock_http_response = MockHttpResponse()
        assertion = _look_up(k, assertions)
        with patch('assert_tools.rest.make_api_call',
                   MagicMock(return_value=mock_http_response(**v))):
            yield assertion, 'http://test.url', v["body"], {}


@patch('assert_tools.rest.make_api_call',
       MagicMock(
           return_value=MockHttpResponse()(status=200, body={123: 'abc'})
       ))
def test_assert_options_request_returns_ok_status_codes():
    """
    Functional tests for
    :py:func:`assert_tools.rest.assert_options_request_returns_ok_status_code`
    """
    rest.assert_options_request_returns_ok_status_code(
        'http://test.url', {'status': 200}, {123: 'abc'}, {})


@patch('assert_tools.rest.make_api_call',
       MagicMock(
           return_value=MockHttpResponse()(status=200, body={})
       ))
def test_assert_head_request_returns_ok_status_codes():
    """
    Functional tests for
    :py:func:`assert_tools.rest.assert_head_request_returns_ok_status_code`
    """
    rest.assert_head_request_returns_ok_status_code(
        'http://test.url', {'status': 200}, {})