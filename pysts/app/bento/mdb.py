from app import n4jdb
from app.bento.node import Node


class MDB:
    """description"""

    def __init__(self, driver=None):
        """Commons

        :param driver:  the driver to connect to mdb neo4j database
        :type driver: a neo4j database driver
        """
        # style N4jdb
        # if driver is None:
        #    n4jdb = N4jdb()
        #    driver = n4jdb.driver

        # style N4jdb_wcm
        if driver is None:
            with n4jdb() as n:
                driver = n

        self.driver = driver

    @staticmethod
    def _get_nodes_query(tx, model=None):
        result = []

        # swap handle to property.handle (vs.handle is null)
        if model is None:
            answers = tx.run(
                """
                MATCH (n:node)
                WHERE n._to IS NULL
                RETURN DISTINCT
                    n.nanoid as nanoid,
                    n.handle as handle,
                    n.model as model
                ORDER BY n.model, n.handle
                """
            )
        else:
            answers = tx.run(
                """
                MATCH (n:node)
                WHERE toLower(n.model) = toLower($model) AND n._to IS NULL
                RETURN DISTINCT
                    n.nanoid as nanoid,
                    n.handle as handle,
                    n.model as model
                ORDER BY n.model, n.handle
                """,
                model=model,
            )

        for record in answers:
            row = (record["id"], record["handle"], record["model"])
            result.append(row)
        return result

    def get_list_of_nodes(self, model=None):
        """notes"""
        list_of_nodes = []
        with self.driver.session() as session:
            list_of_node_records = session.read_transaction(
                self._get_nodes_query, model
            )

            # convert to Node
            for record in list_of_node_records:
                n = Node(
                    handle=record["handle"],
                    nanoid=record["nanoid"],
                    model=record["model"],
                )
                list_of_nodes.append(n)

        return list_of_nodes
