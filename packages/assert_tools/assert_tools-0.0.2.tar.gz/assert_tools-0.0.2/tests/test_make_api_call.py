from mock import patch, MagicMock
from assert_tools import assert_true, rest
from util import MockHttpResponse


def test_make_api_call():
    """
    Test make_api_call
    Unit tests for :py:func:`assert_tools.rest.make_api_call`
    """
    with patch('assert_tools.rest.make_api_call', MagicMock()) as mocked:
        mocked.make_api_call.client.return_value = MockHttpResponse()(
            status=201, body={123: 'abc'})
        rest.make_api_call('http://test.url', 'POST', {})
        assert_true(mocked.called)