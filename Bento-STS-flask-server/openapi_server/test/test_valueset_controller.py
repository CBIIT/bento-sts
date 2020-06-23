# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.term import Term  # noqa: E501
from openapi_server.models.value_set import ValueSet  # noqa: E501
from openapi_server.test import BaseTestCase


class TestValuesetController(BaseTestCase):
    """ValuesetController integration test stubs"""

    def test_get_list_of_value_sets(self):
        """Test case for get_list_of_value_sets

        List all Value Sets
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/valuesets',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_value_set_by_id(self):
        """Test case for get_value_set_by_id

        Get a value set using ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/valuesets/{valueset_id}'.format(valueset_id='valueset_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
