import connexion
import six

from swagger_server import util


def tag_key_value_entities_count_get(key, value, skip=None, limit=None):  # noqa: E501
    """Get number of entities tagged by key:value

     # noqa: E501

    :param key: Tag node key (string)
    :type key: str
    :param value: Tag node value (string)
    :type value: str
    :param skip: Pagination - number of items to skip 
    :type skip: int
    :param limit: Pagination - number of items to return 
    :type limit: int

    :rtype: object
    """
    return 'do some magic!'


def tag_key_value_entities_get(key, value):  # noqa: E501
    """Get list of entities tagged by key:value

     # noqa: E501

    :param key: Tag node key (string)
    :type key: str
    :param value: Tag node value (string)
    :type value: str

    :rtype: object
    """
    return 'do some magic!'


def tag_key_values_get(key):  # noqa: E501
    """Get list of tags having specified tag key

     # noqa: E501

    :param key: Tag node key (string)
    :type key: str

    :rtype: object
    """
    return 'do some magic!'
