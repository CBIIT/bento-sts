# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from openapi_server.models.term import Term  # noqa: E501
from openapi_server.test import BaseTestCase


class TestTermController(BaseTestCase):
    """TermController integration test stubs"""

    def test_get_list_of_terms(self):
        """Test case for get_list_of_terms

        List all terms
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/terms',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_termy_by_id(self):
        """Test case for get_termy_by_id

        Get a property using ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/terms/{term_id}'.format(term_id='term_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
