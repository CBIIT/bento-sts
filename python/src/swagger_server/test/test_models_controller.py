# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.model import Model  # noqa: E501
from swagger_server.test import BaseTestCase


class TestModelsController(BaseTestCase):
    """ModelsController integration test stubs"""

    def test_models_count_get(self):
        """Test case for models_count_get

        Get number of available models
        """
        response = self.client.open(
            '/v1/models/count',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_models_get(self):
        """Test case for models_get

        Get info on available models
        """
        response = self.client.open(
            '/v1/models',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
