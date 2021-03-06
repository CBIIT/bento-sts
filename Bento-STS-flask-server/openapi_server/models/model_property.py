# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.auto import Auto
from openapi_server import util

from openapi_server.models.auto import Auto  # noqa: E501

class ModelProperty(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, handle=None, value_domain=None, model=None, is_required=None):  # noqa: E501
        """ModelProperty - a model defined in OpenAPI

        :param id: The id of this ModelProperty.  # noqa: E501
        :type id: str
        :param handle: The handle of this ModelProperty.  # noqa: E501
        :type handle: str
        :param value_domain: The value_domain of this ModelProperty.  # noqa: E501
        :type value_domain: str
        :param model: The model of this ModelProperty.  # noqa: E501
        :type model: str
        :param is_required: The is_required of this ModelProperty.  # noqa: E501
        :type is_required: Auto
        """
        self.openapi_types = {
            'id': str,
            'handle': str,
            'value_domain': str,
            'model': str,
            'is_required': Auto
        }

        self.attribute_map = {
            'id': 'id',
            'handle': 'handle',
            'value_domain': 'value_domain',
            'model': 'model',
            'is_required': 'is_required'
        }

        self._id = id
        self._handle = handle
        self._value_domain = value_domain
        self._model = model
        self._is_required = is_required

    @classmethod
    def from_dict(cls, dikt) -> 'ModelProperty':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Property of this ModelProperty.  # noqa: E501
        :rtype: ModelProperty
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this ModelProperty.


        :return: The id of this ModelProperty.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ModelProperty.


        :param id: The id of this ModelProperty.
        :type id: str
        """

        self._id = id

    @property
    def handle(self):
        """Gets the handle of this ModelProperty.


        :return: The handle of this ModelProperty.
        :rtype: str
        """
        return self._handle

    @handle.setter
    def handle(self, handle):
        """Sets the handle of this ModelProperty.


        :param handle: The handle of this ModelProperty.
        :type handle: str
        """

        self._handle = handle

    @property
    def value_domain(self):
        """Gets the value_domain of this ModelProperty.


        :return: The value_domain of this ModelProperty.
        :rtype: str
        """
        return self._value_domain

    @value_domain.setter
    def value_domain(self, value_domain):
        """Sets the value_domain of this ModelProperty.


        :param value_domain: The value_domain of this ModelProperty.
        :type value_domain: str
        """

        self._value_domain = value_domain

    @property
    def model(self):
        """Gets the model of this ModelProperty.


        :return: The model of this ModelProperty.
        :rtype: str
        """
        return self._model

    @model.setter
    def model(self, model):
        """Sets the model of this ModelProperty.


        :param model: The model of this ModelProperty.
        :type model: str
        """

        self._model = model

    @property
    def is_required(self):
        """Gets the is_required of this ModelProperty.


        :return: The is_required of this ModelProperty.
        :rtype: Auto
        """
        return self._is_required

    @is_required.setter
    def is_required(self, is_required):
        """Sets the is_required of this ModelProperty.


        :param is_required: The is_required of this ModelProperty.
        :type is_required: Auto
        """

        self._is_required = is_required
