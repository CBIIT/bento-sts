import connexion
import six

from openapi_server.models.model_property import ModelProperty  # noqa: E501
from openapi_server import util


def get_list_of_properties():  # noqa: E501
    """List all properties

    Returns a collection of properties  # noqa: E501


    :rtype: ModelProperty
    """
    return 'do some magic!'


def get_property_by_id(property_id):  # noqa: E501
    """Get a property using ID

    Returns a single property # noqa: E501

    :param property_id: ID of property to return
    :type property_id: str

    :rtype: ModelProperty
    """
    return 'do some magic!'
