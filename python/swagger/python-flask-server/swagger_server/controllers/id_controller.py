import connexion
import six

from swagger_server.models.entity import Entity  # noqa: E501
from swagger_server import util


def id_id_get(id):  # noqa: E501
    """Get MDB entity with specified nanoid

     # noqa: E501

    :param id: Nanoid (6 character unique string)
    :type id: str

    :rtype: Entity
    """
    return 'do some magic!'
