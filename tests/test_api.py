
import unittest
from mock import patch, MagicMock
from crucible import client

import urllib2
import os

def _read_file(filename):
    f = open(os.path.join(os.path.dirname(__file__), filename))
    ret = "".join(f.readlines())
    f.close()
    return ret


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.api = client.API("http://localhost/crucible", "jim", "bob")

    def test_review_url(self):
        self.assertEquals(self.api.review_url("CR-123"), "http://localhost/cru/CR-123")

    @patch("crucible.client.request")
    def test_create_review(self, request_mock):
        response = request_mock.return_value
        response.read.return_value = "<base><permaId>CR-1234</permaId></base>"
        self.api.create_review("title", "description", "project", "JIRA-ISSUE", "moderator")
        body = _read_file("create_review_success_body.xml")
        request_mock.assert_called_once_with('http://localhost/rest-service/reviews-v1', method="POST", 
                            username='jim', password='bob', body=body)

    @patch("crucible.client.request")
    def test_add_reviewers(self, request_mock):
        self.api.add_reviewers("CR-1234", "nbrunson,aglemann")
        request_mock.assert_called_once_with('http://localhost/rest-service/reviews-v1/CR-1234/reviewers', method="POST", 
                            username='jim', password='bob', body="nbrunson,aglemann")

    @patch("crucible.client.request")
    def test_add_patch(self, request_mock):
        self.api.add_patch("CR-1234", "a patch", "repo")
        request_mock.assert_called_once_with('http://localhost/rest-service/reviews-v1/CR-1234/patch', method="POST", 
                            username='jim', password='bob', body=_read_file("add_patch_success_body.xml"))

    @patch("crucible.client.request")
    def test_post_failure(self, request_mock):
        resp = MagicMock()
        resp.read.return_value = "<a><message>You received an error</message></a>"
        request_mock.side_effect = urllib2.HTTPError("Error", 0, 0, 0, resp)
        try:
            ret = self.api._post("url", "body", "error_message")
        except Exception, e:
            self.assertEquals(e.message, "error_message: You received an error")
        else:
            assert False

