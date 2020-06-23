# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.node import Node  # noqa: E501
from openapi_server.test import BaseTestCase


class TestNodeController(BaseTestCase):
    """NodeController integration test stubs"""

    def test_get_list_of_nodes(self):
        """Test case for get_list_of_nodes

        List all nodes 
        """
        query_string = [('modelId', 'model_id_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/nodes',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
