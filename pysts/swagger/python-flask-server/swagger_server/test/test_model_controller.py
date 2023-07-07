# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.model_property import ModelProperty  # noqa: E501
from swagger_server.models.node import Node  # noqa: E501
from swagger_server.test import BaseTestCase


class TestModelController(BaseTestCase):
    """ModelController integration test stubs"""

    def test_model_model_handle_node_node_handle_get(self):
        """Test case for model_model_handle_node_node_handle_get

        Retrieve a specified node from a model
        """
        response = self.client.open(
            '/v1/model/{modelHandle}/node/{nodeHandle}'.format(modelHandle='modelHandle_example', nodeHandle='nodeHandle_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_model_model_handle_node_node_handle_properties_count_get(self):
        """Test case for model_model_handle_node_node_handle_properties_count_get

        Get number of  properties for specified node
        """
        response = self.client.open(
            '/v1/model/{modelHandle}/node/{nodeHandle}/properties/count'.format(modelHandle='modelHandle_example', nodeHandle='nodeHandle_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_model_model_handle_node_node_handle_properties_get(self):
        """Test case for model_model_handle_node_node_handle_properties_get

        Get all properties for specified node
        """
        query_string = [('skip', 56),
                        ('limit', 56)]
        response = self.client.open(
            '/v1/model/{modelHandle}/node/{nodeHandle}/properties'.format(modelHandle='modelHandle_example', nodeHandle='nodeHandle_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_model_model_handle_node_node_handle_property_prop_handle_get(self):
        """Test case for model_model_handle_node_node_handle_property_prop_handle_get

        Retrieve a specified property from a model
        """
        response = self.client.open(
            '/v1/model/{modelHandle}/node/{nodeHandle}/property/{propHandle}'.format(modelHandle='modelHandle_example', nodeHandle='nodeHandle_example', propHandle='propHandle_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_model_model_handle_node_node_handle_property_prop_handle_term_term_value_get(self):
        """Test case for model_model_handle_node_node_handle_property_prop_handle_term_term_value_get

        Retrieve a specified term from a property\\'s acceptable value set 
        """
        response = self.client.open(
            '/v1/model/{modelHandle}/node/{nodeHandle}/property/{propHandle}/term/{termValue}'.format(modelHandle='modelHandle_example', nodeHandle='nodeHandle_example', propHandle='propHandle_example', termValue='termValue_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_model_model_handle_node_node_handle_property_prop_handle_terms_count_get(self):
        """Test case for model_model_handle_node_node_handle_property_prop_handle_terms_count_get

        Get number of  properties for specified node
        """
        response = self.client.open(
            '/v1/model/{modelHandle}/node/{nodeHandle}/property/{propHandle}/terms/count'.format(modelHandle='modelHandle_example', nodeHandle='nodeHandle_example', propHandle='propHandle_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_model_model_handle_node_node_handle_property_prop_handle_terms_get(self):
        """Test case for model_model_handle_node_node_handle_property_prop_handle_terms_get

        Get the terms (acceptable values) for specified property, if applicable to property 
        """
        query_string = [('skip', 56),
                        ('limit', 56)]
        response = self.client.open(
            '/v1/model/{modelHandle}/node/{nodeHandle}/property/{propHandle}/terms'.format(modelHandle='modelHandle_example', nodeHandle='nodeHandle_example', propHandle='propHandle_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_model_model_handle_nodes_count_get(self):
        """Test case for model_model_handle_nodes_count_get

        Get number of nodes for specified model
        """
        response = self.client.open(
            '/v1/model/{modelHandle}/nodes/count'.format(modelHandle='modelHandle_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_model_model_handle_nodes_get(self):
        """Test case for model_model_handle_nodes_get

        Get all nodes for specified model
        """
        query_string = [('skip', 56),
                        ('limit', 56)]
        response = self.client.open(
            '/v1/model/{modelHandle}/nodes'.format(modelHandle='modelHandle_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
