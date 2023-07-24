# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.test import BaseTestCase


class TestTagController(BaseTestCase):
    """TagController integration test stubs"""

    def test_tag_key_value_entities_count_get(self):
        """Test case for tag_key_value_entities_count_get

        Get number of entities tagged by key:value
        """
        query_string = [('skip', 56),
                        ('limit', 56)]
        response = self.client.open(
            '/v1/tag/{key}/{value}/entities/count'.format(key='key_example', value='value_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_tag_key_value_entities_get(self):
        """Test case for tag_key_value_entities_get

        Get list of entities tagged by key:value
        """
        response = self.client.open(
            '/v1/tag/{key}/{value}/entities'.format(key='key_example', value='value_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_tag_key_values_get(self):
        """Test case for tag_key_values_get

        Get list of tags having specified tag key
        """
        response = self.client.open(
            '/v1/tag/{key}/values'.format(key='key_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
