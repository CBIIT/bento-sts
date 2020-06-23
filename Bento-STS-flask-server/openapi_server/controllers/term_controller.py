import connexion
import six

from openapi_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from openapi_server.models.term import Term  # noqa: E501
from openapi_server import util


def get_list_of_terms():  # noqa: E501
    """List all terms

    Returns a collection of terms # noqa: E501


    :rtype: Term
    """
    return 'do some magic!'


def get_termy_by_id(term_id):  # noqa: E501
    """Get a property using ID

    Returns a single property # noqa: E501

    :param term_id: ID of term to return
    :type term_id: str

    :rtype: InlineResponse2001
    """
    return 'do some magic!'
