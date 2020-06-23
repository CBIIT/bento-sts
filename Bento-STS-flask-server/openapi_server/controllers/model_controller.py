import connexion
import six

from openapi_server.models.inline_response200 import InlineResponse200  # noqa: E501
from openapi_server.models.model import Model  # noqa: E501
from openapi_server import util


def get_list_of_models():  # noqa: E501
    """List all models

    Returns a collection of models  # noqa: E501


    :rtype: Model
    """
    return 'do some magic!'


def get_model_by_id(model_id):  # noqa: E501
    """find model by ID

    Returns a single model # noqa: E501

    :param model_id: 
    :type model_id: str

    :rtype: InlineResponse200
    """
    return 'do some magic!'
