# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.entity import Entity  # noqa: E501
from swagger_server.test import BaseTestCase


class TestIdController(BaseTestCase):
    """IdController integration test stubs"""

    def test_id_id_get(self):
        """Test case for id_id_get

        Get MDB entity with specified nanoid
        """
        response = self.client.open(
            '/v1/id/{id}'.format(id='id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
