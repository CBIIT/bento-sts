# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class Tag(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, key: str=None, value: str=None, nanoid: str=None):  # noqa: E501
        """Tag - a model defined in Swagger

        :param key: The key of this Tag.  # noqa: E501
        :type key: str
        :param value: The value of this Tag.  # noqa: E501
        :type value: str
        :param nanoid: The nanoid of this Tag.  # noqa: E501
        :type nanoid: str
        """
        self.swagger_types = {
            'key': str,
            'value': str,
            'nanoid': str
        }

        self.attribute_map = {
            'key': 'key',
            'value': 'value',
            'nanoid': 'nanoid'
        }

        self._key = key
        self._value = value
        self._nanoid = nanoid

    @classmethod
    def from_dict(cls, dikt) -> 'Tag':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Tag of this Tag.  # noqa: E501
        :rtype: Tag
        """
        return util.deserialize_model(dikt, cls)

    @property
    def key(self) -> str:
        """Gets the key of this Tag.


        :return: The key of this Tag.
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key: str):
        """Sets the key of this Tag.


        :param key: The key of this Tag.
        :type key: str
        """
        if key is None:
            raise ValueError("Invalid value for `key`, must not be `None`")  # noqa: E501

        self._key = key

    @property
    def value(self) -> str:
        """Gets the value of this Tag.


        :return: The value of this Tag.
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value: str):
        """Sets the value of this Tag.


        :param value: The value of this Tag.
        :type value: str
        """
        if value is None:
            raise ValueError("Invalid value for `value`, must not be `None`")  # noqa: E501

        self._value = value

    @property
    def nanoid(self) -> str:
        """Gets the nanoid of this Tag.


        :return: The nanoid of this Tag.
        :rtype: str
        """
        return self._nanoid

    @nanoid.setter
    def nanoid(self, nanoid: str):
        """Sets the nanoid of this Tag.


        :param nanoid: The nanoid of this Tag.
        :type nanoid: str
        """
        if nanoid is None:
            raise ValueError("Invalid value for `nanoid`, must not be `None`")  # noqa: E501

        self._nanoid = nanoid
