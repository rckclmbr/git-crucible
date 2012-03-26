
from mock import patch, MagicMock
from crucible import rest
import unittest

class TestRest(unittest.TestCase):

    @patch("crucible.rest.urllib2")
    def test_request(self, urllib2_mock):
        headers={'Content-Type': 'application/xml',
                 "Accept": 'application/xml',
                 "Authorization": "Basic amltOmJvYg==",
               }
        rest.request("http://localhost/", "POST", "body", username="jim", password="bob")
        urllib2_mock.Request.assert_called_once_with(url="http://localhost/", data="body", headers=headers)


