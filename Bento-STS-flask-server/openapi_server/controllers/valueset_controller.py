import connexion
import six

from openapi_server.models.term import Term  # noqa: E501
from openapi_server.models.value_set import ValueSet  # noqa: E501
from openapi_server import util


def get_list_of_value_sets():  # noqa: E501
    """List all Value Sets

    Returns a collection of value sets # noqa: E501


    :rtype: ValueSet
    """
    return 'do some magic!'


def get_value_set_by_id(valueset_id):  # noqa: E501
    """Get a value set using ID

    Returns a single value set # noqa: E501

    :param valueset_id: ID of value set to return
    :type valueset_id: str

    :rtype: Term
    """
    return 'do some magic!'
