import connexion
import six

from openapi_server.models.node import Node  # noqa: E501
from openapi_server import util


def get_node_by_id(node_id):  # noqa: E501
    """Find node by ID

    Returns a single node # noqa: E501

    :param node_id: ID of node to return
    :type node_id: int

    :rtype: Node
    """
    return 'do some magic!'
