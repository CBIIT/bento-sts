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
import datetime

import openapi_client
from openapi_client.models.model_property import ModelProperty  # noqa: E501
from openapi_client.rest import ApiException

class TestModelProperty(unittest.TestCase):
    """ModelProperty unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ModelProperty
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = openapi_client.models.model_property.ModelProperty()  # noqa: E501
        if include_optional :
            return ModelProperty(
                id = '0', 
                handle = '0', 
                value_domain = '0', 
                model = '0', 
                is_required = null
            )
        else :
            return ModelProperty(
        )

    def testModelProperty(self):
        """Test ModelProperty"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
