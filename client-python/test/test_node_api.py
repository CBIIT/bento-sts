# coding: utf-8

"""
    sts

    This is the API for metamodel database  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: mark.benson@nih.gov
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import openapi_client
from openapi_client.api.node_api import NodeApi  # noqa: E501
from openapi_client.rest import ApiException


class TestNodeApi(unittest.TestCase):
    """NodeApi unit test stubs"""

    def setUp(self):
        self.api = openapi_client.api.node_api.NodeApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_list_of_nodes(self):
        """Test case for get_list_of_nodes

        List all nodes   # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
