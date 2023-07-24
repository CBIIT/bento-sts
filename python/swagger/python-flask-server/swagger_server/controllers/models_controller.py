import connexion
import six

from swagger_server.models.model import Model  # noqa: E501
from swagger_server import util


def models_count_get():  # noqa: E501
    """Get number of available models

     # noqa: E501


    :rtype: object
    """
    return 'do some magic!'


def models_get():  # noqa: E501
    """Get info on available models

     # noqa: E501


    :rtype: List[Model]
    """
    return 'do some magic!'
