# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.model_property import ModelProperty  # noqa: E501
from openapi_server.test import BaseTestCase


class TestPropertyController(BaseTestCase):
    """PropertyController integration test stubs"""

    def test_get_list_of_properties(self):
        """Test case for get_list_of_properties

        List all properties
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/properties',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_property_by_id(self):
        """Test case for get_property_by_id

        Get a property using ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/properties/{property_id}'.format(property_id='property_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
