#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Submits diffs to Crucible.
'''


from urlparse import urljoin
import xml.etree.ElementTree as ElementTree
from xml.sax.saxutils import escape
from .rest import request

CREATE_REVIEW_URL = 'rest-service/reviews-v1'
ADD_PATCH_URL = 'rest-service/reviews-v1/%s/patch'
ADD_REVIEWERS_URL = 'rest-service/reviews-v1/%s/reviewers'
APPROVE_URL = 'rest-service/reviews-v1/%s/transition?action=action:approveReview'

CREATE_REVIEW_XML_TEMPLATE = \
"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<createReview>
    <reviewData>
        <allowReviewersToJoin>true</allowReviewersToJoin>
        <author>
            <userName>%s</userName>
        </author>
        <creator>
            <userName>%s</userName>
        </creator>
        <description>%s</description>
        %s
        <moderator>
            <userName>%s</userName>
        </moderator>
        <name>%s</name>
        <projectKey>%s</projectKey>
        <state>Review</state>
        <type>REVIEW</type>
    </reviewData>
</createReview>
"""

ADD_PATCH_XML_TEMPLATE = \
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addPatch>
    <patch>%s</patch>
    <anchor>
        <anchorPath></anchorPath>
        <anchorRepository>%s</anchorRepository>
        <stripCount>1</stripCount>
    </anchor>
</addPatch>
'''

class API(object):

    def __init__(self, host, username, password, verbose=False, debug=False):
        self.username = username
        self.password = password
        self.host = host
        self.verbose = verbose
        self.debug = debug

    def _post(self, url, body, error_message):
        url = urljoin(self.host, url)

        if self.verbose:
            print "URL: %s" % url
            print "Request Body:\n%s" % body
        if self.debug:
            return

        try:
            resp = request(url, method='POST', body=body,
                       headers={'Content-Type': 'application/xml',
                                'Accept': 'application/xml'},
                       username=self.username,
                       password=self.password)
        except HTTPError, e:
            xml = e.read()
            if self.verbose:
                print xml
            message = ElementTree.fromstring(xml).findtext('.//message')
            raise Exception(error_message+": "+message)
        return resp
    
    def add_patch(self, permaid, patch, repository):
        """Add one changeset to the review as a patch."""
        body = ADD_PATCH_XML_TEMPLATE % (escape(patch), escape(repository))
        self._post(ADD_PATCH_URL % permaid, body, "Unable to add patch")

    def add_reviewers(self, permaid, reviewers):
        """Add reviewers to the review."""
        self._post(ADD_REVIEWERS_URL % permaid, reviewers, 
                "Unable to add reviewers '%s' to review" % reviewers)

    def create_review(self, title, description, project, jira_issue=None, moderator=None):
        """
        Creates a new review
        :return the new review's permaId string.
        """
        moderator = moderator if moderator else self.username
        jira_issue = "" if not jira_issue else "<jiraIssueKey>%s</jiraIssueKey>" % escape(jira_issue),

        body = CREATE_REVIEW_XML_TEMPLATE % \
               (escape(self.username), escape(self.username), escape(description), jira_issue,
                escape(moderator), escape(title[:255]), escape(project))
        resp = self._post(CREATE_REVIEW_URL, body, "Unable to create new review")
        if self.debug:
            return "CR-123"
        xml = resp.read()
        return ElementTree.XML(xml).findtext('.//permaId/id')

    def open_review(permaid):
        '''Takes the specified review from Draft to Under Review state.  Not yet 100%.'''
        raise NotImplementedError()
        self._post(APPROVE_URL % permaid)

    def review_url(self, permaid):
        """Returns the crucible url of the review"""
        return urljoin(self.host, "cru/"+permaid)

