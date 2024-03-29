# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class Node(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, handle: str=None, model: str=None, nanoid: str=None):  # noqa: E501
        """Node - a model defined in Swagger

        :param handle: The handle of this Node.  # noqa: E501
        :type handle: str
        :param model: The model of this Node.  # noqa: E501
        :type model: str
        :param nanoid: The nanoid of this Node.  # noqa: E501
        :type nanoid: str
        """
        self.swagger_types = {
            'handle': str,
            'model': str,
            'nanoid': str
        }

        self.attribute_map = {
            'handle': 'handle',
            'model': 'model',
            'nanoid': 'nanoid'
        }

        self._handle = handle
        self._model = model
        self._nanoid = nanoid

    @classmethod
    def from_dict(cls, dikt) -> 'Node':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Node of this Node.  # noqa: E501
        :rtype: Node
        """
        return util.deserialize_model(dikt, cls)

    @property
    def handle(self) -> str:
        """Gets the handle of this Node.


        :return: The handle of this Node.
        :rtype: str
        """
        return self._handle

    @handle.setter
    def handle(self, handle: str):
        """Sets the handle of this Node.


        :param handle: The handle of this Node.
        :type handle: str
        """
        if handle is None:
            raise ValueError("Invalid value for `handle`, must not be `None`")  # noqa: E501

        self._handle = handle

    @property
    def model(self) -> str:
        """Gets the model of this Node.


        :return: The model of this Node.
        :rtype: str
        """
        return self._model

    @model.setter
    def model(self, model: str):
        """Sets the model of this Node.


        :param model: The model of this Node.
        :type model: str
        """
        if model is None:
            raise ValueError("Invalid value for `model`, must not be `None`")  # noqa: E501

        self._model = model

    @property
    def nanoid(self) -> str:
        """Gets the nanoid of this Node.


        :return: The nanoid of this Node.
        :rtype: str
        """
        return self._nanoid

    @nanoid.setter
    def nanoid(self, nanoid: str):
        """Sets the nanoid of this Node.


        :param nanoid: The nanoid of this Node.
        :type nanoid: str
        """
        if nanoid is None:
            raise ValueError("Invalid value for `nanoid`, must not be `None`")  # noqa: E501

        self._nanoid = nanoid
