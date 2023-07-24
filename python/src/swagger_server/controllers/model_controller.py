import connexion
import six

from swagger_server.models.model_property import ModelProperty  # noqa: E501
from swagger_server.models.node import Node  # noqa: E501
from swagger_server import util


def model_model_handle_node_node_handle_get(modelHandle, nodeHandle):  # noqa: E501
    """Retrieve a specified node from a model

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str
    :param nodeHandle: Handle (\\&#39;name\\&#39;) of node (use /model/{modelHandle}/nodes to find available nodes 
    :type nodeHandle: str

    :rtype: Node
    """
    return 'do some magic!'


def model_model_handle_node_node_handle_properties_count_get(modelHandle, nodeHandle):  # noqa: E501
    """Get number of  properties for specified node

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str
    :param nodeHandle: Handle (\\&#39;name\\&#39;) of node (use /model/{modelHandle}/nodes to find available nodes 
    :type nodeHandle: str

    :rtype: object
    """
    return 'do some magic!'


def model_model_handle_node_node_handle_properties_get(modelHandle, nodeHandle, skip=None, limit=None):  # noqa: E501
    """Get all properties for specified node

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str
    :param nodeHandle: Handle (\\&#39;name\\&#39;) of node (use /model/{modelHandle}/nodes to find available nodes 
    :type nodeHandle: str
    :param skip: Pagination - number of items to skip 
    :type skip: int
    :param limit: Pagination - number of items to return 
    :type limit: int

    :rtype: object
    """
    return 'do some magic!'


def model_model_handle_node_node_handle_property_prop_handle_get(modelHandle, nodeHandle, propHandle):  # noqa: E501
    """Retrieve a specified property from a model

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str
    :param nodeHandle: Handle (\\&#39;name\\&#39;) of node (use /model/{modelHandle}/nodes to find available nodes 
    :type nodeHandle: str
    :param propHandle: Handle (\\&#39;name\\&#39;) of property (use /model/{modelHandle}/node/{nodeHandle}/properties to find available properties 
    :type propHandle: str

    :rtype: ModelProperty
    """
    return 'do some magic!'


def model_model_handle_node_node_handle_property_prop_handle_term_term_value_get(modelHandle, nodeHandle, propHandle, termValue):  # noqa: E501
    """Retrieve a specified term from a property\\&#39;s acceptable value set 

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str
    :param nodeHandle: Handle (\\&#39;name\\&#39;) of node (use /model/{modelHandle}/nodes to find available nodes 
    :type nodeHandle: str
    :param propHandle: Handle (\\&#39;name\\&#39;) of property (use /model/{modelHandle}/node/{nodeHandle}/properties to find available properties 
    :type propHandle: str
    :param termValue: String representation (\\&#39;value\\&#39;) of the term (use /model/{modelHandle}/node/{nodeHandle}/property/{propHandle}/terms to find available terms 
    :type termValue: str

    :rtype: object
    """
    return 'do some magic!'


def model_model_handle_node_node_handle_property_prop_handle_terms_count_get(modelHandle, nodeHandle, propHandle):  # noqa: E501
    """Get number of  properties for specified node

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str
    :param nodeHandle: Handle (\\&#39;name\\&#39;) of node (use /model/{modelHandle}/nodes to find available nodes 
    :type nodeHandle: str
    :param propHandle: Handle (\\&#39;name\\&#39;) of property (use /model/{modelHandle}/node/{nodeHandle}/properties to find available properties 
    :type propHandle: str

    :rtype: object
    """
    return 'do some magic!'


def model_model_handle_node_node_handle_property_prop_handle_terms_get(modelHandle, nodeHandle, propHandle, skip=None, limit=None):  # noqa: E501
    """Get the terms (acceptable values) for specified property, if applicable to property 

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str
    :param nodeHandle: Handle (\\&#39;name\\&#39;) of node (use /model/{modelHandle}/nodes to find available nodes 
    :type nodeHandle: str
    :param propHandle: Handle (\\&#39;name\\&#39;) of property (use /model/{modelHandle}/node/{nodeHandle}/properties to find available properties 
    :type propHandle: str
    :param skip: Pagination - number of items to skip 
    :type skip: int
    :param limit: Pagination - number of items to return 
    :type limit: int

    :rtype: object
    """
    return 'do some magic!'


def model_model_handle_nodes_count_get(modelHandle):  # noqa: E501
    """Get number of nodes for specified model

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str

    :rtype: object
    """
    return 'do some magic!'


def model_model_handle_nodes_get(modelHandle, skip=None, limit=None):  # noqa: E501
    """Get all nodes for specified model

     # noqa: E501

    :param modelHandle: Handle (\\&#39;name\\&#39;) of model (use /models to find available handles) 
    :type modelHandle: str
    :param skip: Pagination - number of items to skip 
    :type skip: int
    :param limit: Pagination - number of items to return 
    :type limit: int

    :rtype: object
    """
    return 'do some magic!'
