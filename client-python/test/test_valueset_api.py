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
from openapi_client.api.valueset_api import ValuesetApi  # noqa: E501
from openapi_client.rest import ApiException


class TestValuesetApi(unittest.TestCase):
    """ValuesetApi unit test stubs"""

    def setUp(self):
        self.api = openapi_client.api.valueset_api.ValuesetApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_list_of_value_sets(self):
        """Test case for get_list_of_value_sets

        List all Value Sets  # noqa: E501
        """
        pass

    def test_get_value_set_by_id(self):
        """Test case for get_value_set_by_id

        Get a value set using ID  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
