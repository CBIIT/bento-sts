import connexion
import six

from openapi_server.models.node import Node  # noqa: E501
from openapi_server import util


def get_list_of_nodes(model_id=None):  # noqa: E501
    """List all nodes 

    Returns a collection of nodes # noqa: E501

    :param model_id: limit to nodes belonging to this model 
    :type model_id: str

    :rtype: Node
    """
    return 'do some magic!'
