# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.inline_response200 import InlineResponse200  # noqa: E501
from openapi_server.models.model import Model  # noqa: E501
from openapi_server.test import BaseTestCase


class TestModelController(BaseTestCase):
    """ModelController integration test stubs"""

    def test_get_list_of_models(self):
        """Test case for get_list_of_models

        List all models
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/models',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_model_by_id(self):
        """Test case for get_model_by_id

        find model by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/models/{model_id}'.format(model_id='model_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
