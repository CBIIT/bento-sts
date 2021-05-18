import os
import pprint
import json
from collections import namedtuple
from operator import attrgetter
from app import db, logging
from flask import url_for, current_app
from neo4j import GraphDatabase
from bento_meta.model import Model
from bento_meta.object_map import ObjectMap


class mdb:
    def __init__(self):
        # self.uri = uri if uri is not None else os.environ.get('NEO4J_MDB_URI')
        # self.user = user if user is not None else os.environ.get('NEO4J_MDB_USER')
        # self.password = password if password is not None else os.environ.get('NEO4J_MDB_PASS')
        self.uri = os.environ.get("NEO4J_MDB_URI")
        self.user = os.environ.get("NEO4J_MDB_USER")
        self.password = os.environ.get("NEO4J_MDB_PASS")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    @staticmethod
    def _get_models_query(tx):
        list_of_models = []
        result = tx.run("MATCH (n:node) WHERE n._to IS NULL RETURN DISTINCT n.model as model")
        for record in result:
            list_of_models.append(record["model"])
        return list_of_models

    """
    In [5]: m.get_list_of_models()
    Out[5]: ['ICDC', 'CTDC']
    """

    def get_list_of_models(self):
        with self.driver.session() as session:
            models = session.read_transaction(self._get_models_query)
        return models

    """
    In [4]: m.get_model_by_name('ICDC')
    Out[4]: <bento_meta.model.Model at 0x110378450>
    """

    def get_model_by_name(self, name):
        ObjectMap.clear_cache()
        model = Model(name, self.driver)
        # if you dont call dget, it wont be populated...
        model.dget()
        return model

    # ############################################################################################### #
    # NODES
    # ############################################################################################### #
    @staticmethod
    def _get_node_by_id_query(tx, nid, model=None):

        # // idea: n3 -> n1 --> n2
        result = {}
        _seen_properties = []   # for convenience tracking

        query = ""

        if model is not None:
            query = """
            MATCH (n1:node)
            WHERE n1.nanoid = $nid
            WHERE toLower(n1.model) = toLower($model)
            AND n1._to IS NULL
            OPTIONAL MATCH (n1)<-[:has_src]-(r12:relationship)-[:has_dst]->(n2:node)
                WHERE NOT (n2._to is NOT NULL) and NOT (r12._to IS NOT NULL)
            OPTIONAL MATCH (n3)<-[:has_src]-(r31:relationship)-[:has_dst]->(n1:node)
                WHERE NOT (n3._to is NOT NULL) and NOT (r31._to IS NOT NULL)
            OPTIONAL MATCH (n1)-[:has_property]->(p1:property)
                WHERE NOT (p1._to is NOT NULL)
            OPTIONAL MATCH (n1)-[:has_concept]->(c1:concept)
                WHERE NOT (c1._to IS NOT NULL)
            OPTIONAL MATCH (ct:term)-[:represents]->(c1)
                WHERE NOT (ct._to IS NOT NULL)
            OPTIONAL MATCH (ct)-[:has_origin]->(o:origin)
                WHERE NOT (o._to IS NOT NULL)
            RETURN DISTINCT n1.nanoid as n1_id,
                        n1.handle as n1_handle,
                        n1.model as n1_model,
                        r12.nanoid as r12_id,
                        r12.handle as r12_handle,
                        n2.nanoid as n2_id,
                        n2.handle  as n2_handle,
                        n2.model   as n2_model,
                        r31.nanoid    as r31_id,
                        r31.handle as r31_handle,
                        n3.nanoid as n3_id,
                        n3.handle  as n3_handle,
                        n3.model   as n3_model,
                        p1.nanoid as p1_id,
                        p1.handle  as p1_handle,
                        p1.value_domain as p1_value_domain,
                        p1.model as p1_model
                        """
        else:
            query = """
            MATCH (n1:node)
            WHERE n1.nanoid = $nid
            AND n1._to IS NULL
            OPTIONAL MATCH (n1)<-[:has_src]-(r12:relationship)-[:has_dst]->(n2:node)
                WHERE NOT (n2._to is NOT NULL) and NOT (r12._to IS NOT NULL)
            OPTIONAL MATCH (n3)<-[:has_src]-(r31:relationship)-[:has_dst]->(n1:node)
                WHERE NOT (n3._to is NOT NULL) and NOT (r31._to IS NOT NULL)
            OPTIONAL MATCH (n1)-[:has_property]->(p1:property)
                WHERE NOT (p1._to is NOT NULL)
            OPTIONAL MATCH (n1)-[:has_concept]->(c1:concept)
                WHERE NOT (c1._to IS NOT NULL)
            OPTIONAL MATCH (ct:term)-[:represents]->(c1)
                WHERE NOT (ct._to IS NOT NULL)
            OPTIONAL MATCH (ct)-[:has_origin]->(o:origin)
                WHERE NOT (o._to IS NOT NULL)
            RETURN DISTINCT n1.nanoid as n1_id,
                        n1.handle as n1_handle,
                        n1.model as n1_model,
                        r12.nanoid as r12_id,
                        r12.handle as r12_handle,
                        n2.nanoid as n2_id,
                        n2.handle  as n2_handle,
                        n2.model   as n2_model,
                        r31.nanoid    as r31_id,
                        r31.handle as r31_handle,
                        n3.nanoid as n3_id,
                        n3.handle  as n3_handle,
                        n3.model   as n3_model,
                        p1.nanoid as p1_id,
                        p1.handle  as p1_handle,
                        p1.value_domain as p1_value_domain,
                        p1.model as p1_model
                        """

        answer = tx.run(query, nid=nid, model=model)

        for record in answer:

            # A. if result{} is empty (first time through) then initialize
            if not bool(result):
                result = {
                    "id": record["n1_id"],
                    "handle": record["n1_handle"],
                    "model": record["n1_model"],
                    "desc": "desc",
                    "link": url_for('main.nodes', id=record["n1_id"]),
                    "type": "node",
                }

            # B. if "from node" exists
            if bool(record["n3_id"]):
                if "has_relationship_from_nodes" not in result.keys():
                    result["has_relationship_from_nodes"] = []

                from_node = {
                    "id": record["n3_id"],
                    "handle": record["n3_handle"],
                    "link": url_for('main.nodes', id=record["n3_id"]),
                    "type": "node",
                    "relationship": {
                        "id": record["r31_id"],
                        "handle": record["r31_handle"],
                        "link": "/relationships/" + record["r31_id"],
                        "type": "relationship",
                    },
                }

                # see if we need to add this node
                unique = True
                from_node_ = json.dumps(from_node, sort_keys=True)
                for other_node in result["has_relationship_from_nodes"]:
                    other_node_ = json.dumps(other_node, sort_keys=True)
                    if other_node_ == from_node_:
                        unique = False
                        break
                if unique:
                    result["has_relationship_from_nodes"].append(from_node)

            # C. if "to node" exists
            if bool(record["n2_id"]):
                if "has_relationship_to_nodes" not in result.keys():
                    result["has_relationship_to_nodes"] = []

                to_node = {
                    "id": record["n2_id"],
                    "handle": record["n2_handle"],
                    "link": url_for('main.nodes', id=record["n2_id"]),
                    "type": "node",
                    "relationship": {
                        "id": record["r12_id"],
                        "handle": record["r12_handle"],
                        "link": "/relationships/" + record["r12_id"],
                        "type": "relationship",
                    },
                }

                # see if we need to add this node
                unique = True
                to_node_ = json.dumps(to_node, sort_keys=True)
                for other_node in result["has_relationship_to_nodes"]:
                    other_node_ = json.dumps(other_node, sort_keys=True)
                    if other_node_ == to_node_:
                        unique = False
                        break
                if unique:
                    result["has_relationship_to_nodes"].append(to_node)

            # D. if there are properties
            if record["p1_id"]:

                if "has_properties" not in result.keys():
                    result["has_properties"] = []

                if record["p1_id"] not in _seen_properties:
                    property_ = {
                        "id": record["p1_id"],
                        "handle": record["p1_handle"],
                        "type": "property",
                        "link": url_for('main.properties', id=record["p1_id"]),
                        "value_domain": record["p1_value_domain"]
                    }
                    _seen_properties.append(record["p1_id"])
                    result["has_properties"].append(property_)

        return result

    def get_node_by_id(self, nid, model=None):
        with self.driver.session() as session:
            node_ = session.read_transaction(self._get_node_by_id_query, nid, model)
        return node_

    # ------------------------------------------------------------------------- #
    def get_list_of_nodes_bento(self):
        """
        In [3]: m.get_list_of_nodes()
        {'ICDC': {'case': <bento_meta.objects.Node at 0x110226bd0>,
        'off_study': <bento_meta.objects.Node at 0x110194b10>,
        'file': <bento_meta.objects.Node at 0x1101fb1d0>,
        'diagnosis': <bento_meta.objects.Node at 0x1101f91d0>,
        'image': <bento_meta.objects.Node at 0x110194690>,
        'assay': <bento_meta.objects.Node at 0x1101f7f90>,
        'prior_surgery': <bento_meta.objects.Node at 0x1102>},
        'CTDC': {'sequencing_assay': <bento_meta.objects.Node at 0x1102e8350>,
        'nucleic_acid': <bento_meta.objects.Node at 0x1102eb650>,
        """
        result = {}
        ObjectMap.clear_cache()
        models = self.get_list_of_models()
        for model in models:
            localmodel = self.get_model_by_name(model)
            result[model] = localmodel.nodes
        return result

    # ------------------------------------------------------------------------- #
    @staticmethod
    def _get_list_of_nodes_query(tx, model=None):
        result = []

        # swap handle to property.handle (vs.handle is null)
        if model is None:
            answers = tx.run(
                """
                MATCH (n:node)
                WHERE n._to IS NULL
                RETURN DISTINCT
                    n.nanoid as id,
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
                    n.nanoid as id,
                    n.handle as handle,
                    n.model as model
                ORDER BY n.model, n.handle
                """, model=model
            )

        for record in answers:
            # row = {record["id"]: record["handle"]}
            row = (record["id"], record["handle"], record['model'])
            result.append(row)
        return result

    def get_list_of_nodes(self, model=None):
        """
        In [3]: m.get_list_of_nodes()
        Out[3]:
        [{'yXWr0Y': 'study_site'},
         {'N0Qx7Z': 'off_study'},
         {'nUoHJH': 'diagnosis
        """
        with self.driver.session() as session:
            list_o_dicts = session.read_transaction(self._get_list_of_nodes_query, model)
        return list_o_dicts

    # ========================================================================= #
    @staticmethod
    def _do_update_node(tx, neo4jquery, nid, nhandle):
        result = []

        answers = tx.run(neo4jquery, nid=nid, nhandle=nhandle)

        for record in answers:
            result.append(record)
        return result

    def get_query_to_update_node(self):
        return '''
                MATCH (n1:node)
                WHERE n1.nanoid = $nid and n1._to IS NULL
                CALL apoc.refactor.cloneNodesWithRelationships([n1])
                YIELD input, output
                MATCH (n2:node)
                where n2.nanoid = $nid and n2._to IS NULL and id(n1) <> id(n2)
                SET n1._to = ( n1._from + 1 ), n2._from = (n1._from + 1), n2.handle = $nhandle
                RETURN id(n2)
                '''

    def update_node_by_id(self, nid, nhandle):
        with self.driver.session() as session:
            pprint.pprint('trying to run update node on {} and {}'.format(nid, nhandle))
            query = self.get_query_to_update_node()
            node_ = session.write_transaction(self._do_update_node, query, nid, nhandle)
            # TODO update elasticsearch, remove old handle and add new
        return node_

    # ############################################################################################### #
    # VALUESETS
    # ############################################################################################### #
    def get_query_for_valueset_by_id(self, model=None):
        querystring = ""

        if model is None:
            querystring = """
            MATCH (vs:value_set)
            WHERE vs.nanoid = $vsid and vs._to IS NULL
            MATCH (p:property)-[:has_value_set]->(vs) 
                WHERE NOT (p._to IS NOT NULL)
            OPTIONAL MATCH (p)-[:has_concept]->(cp:concept)
                WHERE NOT (p._to IS NOT NULL) AND NOT (cp._to IS NOT NULL)
            OPTIONAL MATCH (ct:term)-[:represents]->(cp)
                WHERE NOT (ct._to IS NOT NULL)
            OPTIONAL MATCH (vs)-[:has_term]->(t:term)
                WHERE NOT (t._to IS NOT NULL)
            OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
                WHERE NOT (cto._to IS NOT NULL)
            OPTIONAL MATCH (vs)-[:has_origin]->(vso:origin)
                WHERE NOT (vso._to IS NOT NULL)
            RETURN DISTINCT
                p.nanoid as property_id,
                p.handle as property_handle,
                p.model as property_model,
                vs.nanoid as vs_id,
                vs.url as vs_url,
                vs.handle as vs_handle,
                t.nanoid as term_id,
                t.value as term_value
            """
        else:
            querystring = """
            MATCH (vs:value_set)
            WHERE vs.nanoid = $vsid and vs._to IS NULL
            MATCH (p:property)-[:has_value_set]->(vs)
            WHERE toLower(p.model) = toLower($model) AND NOT (p._to IS NOT NULL)
            OPTIONAL MATCH (p)-[:has_concept]->(cp:concept)
                WHERE NOT (p._to IS NOT NULL) AND NOT (cp._to IS NOT NULL)
            OPTIONAL MATCH (ct:term)-[:represents]->(cp)
                WHERE NOT (ct._to IS NOT NULL)
            OPTIONAL MATCH (vs)-[:has_term]->(t:term)
                WHERE NOT (t._to IS NOT NULL)
            OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
                WHERE NOT (cto._to IS NOT NULL)
            OPTIONAL MATCH (vs)-[:has_origin]->(vso:origin)
                WHERE NOT (vso._to IS NOT NULL)
            RETURN DISTINCT
                p.nanoid as property_id,
                p.handle as property_handle,
                p.model as property_model,
                vs.nanoid as vs_id,
                vs.url as vs_url,
                vs.handle as vs_handle,
                t.nanoid as term_id,
                t.value as term_value
            """
        return querystring

    @staticmethod
    def _do_query_for_valueset_by_id(tx, neo4jquery, vsid, model=None):
        result = {}
        _seen_terms = []  # for convenience tracking

        answers = tx.run(neo4jquery, vsid=vsid, model=model)

        for record in answers:

            # A. if result{} is empty (first time through) then initialize
            if not bool(result):
                result = {
                    "id": record["vs_id"],
                    "handle": record["property_handle"],
                    "model": record["property_model"],
                    "url": record["vs_url"],
                    "desc": "desc",
                    "type": "valueset",
                    "link": url_for('main.valuesets', id=record["vs_id"]),
                    "_for_propertyhandle": record["property_handle"],
                    "_for_propertyid": record["property_id"]
                }

            # B. add property
            if record["property_id"]:
                if "has_property" not in result.keys():
                    result["has_property"] = {
                        "id": record["property_id"],
                        "handle": record["property_handle"],
                        "type": "property",
                        "link": "/properties/" + record["property_id"],
                    }

            # C. skip origin

            # D. add terms
            if record["term_id"]:

                if "has_terms" not in result.keys():
                    result["has_terms"] = []

                if record["term_id"] not in _seen_terms:
                    term_ = {
                        "id": record["term_id"],
                        "value": record["term_value"],
                        "type": "term",
                        "link": url_for('main.terms', id=record["term_id"]),
                    }
                    _seen_terms.append(record["term_id"])
                    result["has_terms"].append(term_)

        return result

    def get_valueset_by_id(self, vsid, model=None):
        with self.driver.session() as session:
            query = self.get_query_for_valueset_by_id(model)
            vs = session.read_transaction(self._do_query_for_valueset_by_id, query, vsid, model)
        return vs

    # ------------------------------------------------------------------------- #
    @staticmethod
    def _do_query_for_list_of_valuesets(tx, neo4jquery, model):
        result = []

        answers = tx.run(neo4jquery, model=model)

        for record in answers:
            row = {record["id"]: record["handle"]}
            result.append(row)

        return result

    def get_query_for_list_of_valuesets(self, model):
        if model is None:
            return """MATCH (vs:value_set)<-[:has_value_set]-(p:property)
                      WHERE vs._to IS NULL and p._to IS NULL
                      RETURN DISTINCT vs.nanoid as id, p.handle as handle"""
        else:
            return """MATCH (vs:value_set)<-[:has_value_set]-(p:property)
                      WHERE toLower(p.model) = toLower($model) and vs._to IS NULL and p._to IS NULL
                      RETURN DISTINCT vs.nanoid as id, p.handle as handle"""

    def get_list_of_valuesets(self, model=None):
        with self.driver.session() as session:
            query = self.get_query_for_list_of_valuesets(model)
            list_o_dicts = session.read_transaction(self._do_query_for_list_of_valuesets, query, model)
        return list_o_dicts

    # ############################################################################################### #
    # TERMS
    # ############################################################################################### #

    @staticmethod
    def _get_term_by_id_query(tx, tid):
        result = {}
        answer = tx.run(
            """
            MATCH (t:term) 
            WHERE t.nanoid = $tid AND t._to IS NULL
            OPTIONAL MATCH (t)-[:has_origin]->(to:origin)
            WHERE to._to IS NULL
            RETURN DISTINCT
                t.nanoid as id,
                t.value as value,
                t.desc as desc,
                t.origin_definition as origin_definition,
                t.origin_id as origin_id,
                to.nanoid as originid,
                to.name as originname
            """,
            tid=tid,
        )

        for record in answer:
            # format into json structure
            result = {
                "id": record["id"],
                "value": record["value"],
                "desc": record["desc"],
                "origin_definition": record["origin_definition"],
                "origin_id": record["origin_id"],
                "type": "term",
                "link": url_for("main.terms", id=record["id"], _external=False),
                "has_origin": {
                    "id": record["originid"],
                    "name": record["originname"],
                    "type": "origin",
                    "link": "/origins/" + record["originid"],
                },
            }
        return result
    # ------------------------------------------------------------------------- #

    def get_term_by_id(self, tid):
        with self.driver.session() as session:
            term_ = session.read_transaction(self._get_term_by_id_query, tid)
        return term_

    # ========================================================================= #

    @staticmethod
    def _get_list_of_terms_query(tx, model=None):
        result = []

        if model is None:
            answers = tx.run(
                """
                MATCH (p)-[:has_value_set]->(vs)
                MATCH (vs)-[:has_term]->(t:term)
                WHERE p._to IS NULL and vs._to IS NULL and t._to IS NULL
                RETURN DISTINCT
                    t.nanoid as id,
                    t.value as value,
                    p.handle as handle,
                    p.model as model,
                    p.nanoid as pid
                ORDER BY model, handle, value
                """
            )
        else:
            answers = tx.run(
                """
                MATCH (p)-[:has_value_set]->(vs)
                MATCH (vs)-[:has_term]->(t:term)
                WHERE p._to IS NULL and vs._to IS NULL and t._to IS NULL and toLower(p.model) = toLower($model)
                RETURN DISTINCT
                    t.nanoid as id,
                    t.value as value,
                    p.handle as handle,
                    p.model as model,
                    p.nanoid as pid
                ORDER BY model, handle, value
                """, model=model
            )

        for record in answers:
            # row = {record["id"]: record["value"]}
            row = (record["id"], record["value"], record['model'], record['handle'], record['pid'])
            result.append(row)
        return result

    def get_list_of_terms(self, model=None):
        with self.driver.session() as session:
            list_o_dicts = session.read_transaction(self._get_list_of_terms_query, model)
        return list_o_dicts

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _do_update_term(tx, neo4jquery, tid, tvalue):
        print("working with tid {} for {}".format(tid, tvalue))
        result = []

        answers = tx.run(neo4jquery, tid=tid, tvalue=tvalue)

        for record in answers:
            # row = {record["id(t2)"]: record["handle"]}
            result.append(record)
        return result

    def get_query_to_update_term(self):
        return '''
                MATCH (t1:term)
                WHERE t1.nanoid = $tid and t1._to IS NULL
                CALL apoc.refactor.cloneNodesWithRelationships([t1])
                YIELD input, output
                MATCH (t2:term)
                where t2.nanoid = $tid and t2._to IS NULL and id(t1) <> id (t2)
                SET t1._to = ( t1._from + 1 ), t2._from = (t1._from + 1), t2.value = $tvalue
                RETURN id(t2)
                '''

    def update_term_by_id(self, tid, tvalue):
        with self.driver.session() as session:
            query = self.get_query_to_update_term()
            term_ = session.write_transaction(self._do_update_term, query, tid, tvalue)
            # TODO update elasticsearch, remove old term and add new term
        return term_

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _do_create_term(tx, neo4jquery, tvalue):
        print("working with for {}".format(tvalue))
        result = []

        answers = tx.run(neo4jquery, tvalue=tvalue)

        for record in answers:
            result.append(record)
        return result

    def get_query_to_create_term(self):
        return '''
                MATCH (t1:term)
                WHERE t1.value = $tvalue and t1._to IS NULL
                SET t1._to = ( t1._from + 1 ), t2._from = (t1._from + 1), t2.value = $tvalue
                RETURN id(t2);
                '''

    def create_term(self, tvalue):
        with self.driver.session() as session:
            query = self.get_query_to_create_term()
            term_ = session.write_transaction(self._do_create_term, query, tvalue)
            # TODO update elasticsearch add new term
        return term_

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _do_deprecate_term(tx, neo4jquery, tid):
        print("deprecating term {}".format(tid))
        result = []

        answers = tx.run(neo4jquery, tid=tid)

        for record in answers:
            result.append(record)
        return result

    def get_query_to_deprecate_term(self):
        return '''
                MATCH (t1:term)
                WHERE t1.nanoid = $tid and t1._to IS NULL
                SET t1._to = ( t1._from + 1 )
                RETURN id(t1);
                '''

    def deprecate_term(self, tid):
        with self.driver.session() as session:
            query = self.get_query_to_deprecate_term()
            term_ = session.write_transaction(self._do_deprecate_term, query, tid)
            # TODO update elasticsearch, remove old term
        return term_

    # ############################################################################################### #
    # ORIGINS
    # ############################################################################################### #

    @staticmethod
    def _get_list_of_origins_query(tx):
        result = []
        # only get those terms associated with valuesets (some terms assoc w/ concepts)
        answers = tx.run(
            "MATCH (o:origin)"
            "RETURN DISTINCT"
            "    o.nanoid as id, "
            "    o.name as name "
        )
        for record in answers:
            # pprint.pprint("---")
            # pprint.pprint(record['id'])
            # pprint.pprint(record['value'])
            row = {record["id"]: record["name"]}
            result.append(row)
        return result

    """
    In [3]: m.get_list_of_origins()
    Out[3]:
    [{'kcmuEa': 'ICDC'},
     {'2vT78W': 'CTDC'},
     {'8YaZWJ': 'NCIT'},
     {'pqZesz': 'BRIDG'}]
    """

    def get_list_of_origins(self):
        with self.driver.session() as session:
            list_o_dicts = session.read_transaction(self._get_list_of_origins_query)
        return list_o_dicts

    # ############################################################################################### #
    # PROPERTIES
    # ############################################################################################### #

    @staticmethod
    def _get_list_of_properties_query(tx, model=None):
        result = []

        if model is None:
            answers = tx.run(
                """
                MATCH (n:node)-[:has_property]->(p:property)
                WHERE p._to IS NULL and n._to IS NULL
                RETURN DISTINCT
                p.nanoid as id,
                p.handle as handle,
                p.model as property_model,
                n.nanoid as nid,
                n.handle as nhandle
                ORDER BY property_model, handle
                """
            )
        else:
            answers = tx.run(
                """
                MATCH (n:node)-[:has_property]->(p:property)
                WHERE toLower(p.model) = toLower($model) and p._to IS NULL and n._to IS NULL
                RETURN DISTINCT
                p.nanoid as id,
                p.handle as handle,
                p.model as property_model,
                n.nanoid as nid,
                n.handle as nhandle
                ORDER BY property_model, handle
                """, model=model
            )

        for record in answers:
            # row = {record["id"]: record["handle"]}
            row = (record["id"], record["handle"], record['property_model'], record['nhandle'], record['nid'])
            result.append(row)
        return result

    def get_list_of_properties(self, model=None):
        with self.driver.session() as session:
            
            list_o_dicts = session.read_transaction(self._get_list_of_properties_query, model)
        return list_o_dicts

    @staticmethod
    def _get_property_by_id_query(tx, pid, model=None):
        result = {}
        _seen_terms = []

        # only get those terms associated with valuesets (some terms assoc w/ concepts)
        if model is None:
            answers = tx.run(
                """
                MATCH (p:property)
                WHERE p.nanoid = $pid
                OPTIONAL MATCH (n)-[:has_property]->(p)
                OPTIONAL MATCH (p)-[:has_value_set]->(vs)
                OPTIONAL MATCH (vs)-[:has_term]->(t:term)
                RETURN DISTINCT
                p.nanoid as id,
                p.handle as handle,
                p.model as model,
                p.value_domain as value_domain,
                p.is_required as isrequired,
                n.handle as nodehandle,
                n.nanoid as nodeid,
                vs.nanoid as valueset_id,
                t.nanoid as term_id,
                t.value as term_value,
                COUNT(DISTINCT(t.nanoid))
                """,
                pid=pid,
            )
        else:
            answers = tx.run(
                """
                MATCH (p:property)
                WHERE p.nanoid = $pid
                WHERE n.model = $model
                OPTIONAL MATCH (n)-[:has_property]->(p)
                OPTIONAL MATCH (p)-[:has_value_set]->(vs)
                OPTIONAL MATCH (vs)-[:has_term]->(t:term)
                RETURN DISTINCT
                p.nanoid as id,
                p.handle as handle,
                p.model as model,
                p.value_domain as value_domain,
                p.is_required as isrequired,
                n.handle as nodehandle,
                n.nanoid as nodeid,
                vs.nanoid as valueset_id,
                t.nanoid as term_id,
                t.value as term_value,
                COUNT(DISTINCT(t.nanoid))
                """,
                pid=pid, model=model
            )

        for record in answers:

            # A. if result{} is empty (first time through) then initialize
            if not bool(result):
                result = {
                    "id": record["id"],
                    "handle": record["handle"],
                    "model": record["model"],
                    "value_domain": record["value_domain"],
                    "is_required": record["isrequired"],
                    "type": "property",
                    "link": "/properties/" + record["id"],
                    "_for_nodehandle": record["nodehandle"],
                    "_for_nodeid": record["nodeid"],
                }

            # B. add valueset
            if record["valueset_id"]:
                if "has_valueset" not in result.keys():
                    result["has_valueset"] = {
                        "id": record["valueset_id"],
                        "type": "valueset",
                        "link": url_for("main.valuesets", id=record["valueset_id"]),
                    }

            # C. skip origin

            # D. add terms
            if record["term_id"]:

                if "has_terms" not in result.keys():
                    result["has_terms"] = []

                if record["term_id"] not in _seen_terms:
                    term_ = {
                        "id": record["term_id"],
                        "value": record["term_value"],
                        "type": "term",
                        "link": url_for("main.terms", id=record["term_id"]),
                    }
                    _seen_terms.append(record["term_id"])
                    result["has_terms"].append(term_)

        return result

    def get_property_by_id(self, pid, model=None):
        with self.driver.session() as session:
            property_ = session.read_transaction(self._get_property_by_id_query, pid, model)
        return property_






    @staticmethod
    def _get_tags_from_db(tx, model=None):
        result = []

        current_app.logger.warn('yup... using model {}'.format(model))

        query_against_all_models = """
                MATCH (n:node) -[:has_property]->(p:property)-[:has_tag]->(t:tag)
                RETURN n.handle, n.nanoid, p.handle, p.nanoid, t.key, t.value;
                """
        query_against_specific_model = """
                MATCH (n:node) -[:has_property]->(p:property)-[:has_tag]->(t:tag)
                WHERE toLower(n.model) = toLower($model)
                RETURN n.handle, n.nanoid, p.handle, p.nanoid, t.key, t.value;
                """

        db_records = None
        if model is None:
            db_records = tx.run(query_against_all_models,)
            current_app.logger.warn(' point 2 ... using model {}'.format(model))
        else:
            db_records = tx.run(query_against_specific_model, model=model)
            current_app.logger.warn(' point 3 ... using model {}'.format(model))
        for record in db_records:
            result.append(record)

        return result

    def get_tags(self, model=None):
        with self.driver.session() as session:
            current_app.logger.warn('have model {}'.format(model))
            tag_records = session.read_transaction(self._get_tags_from_db, model)
            formatted_tags = self.format_tags_records(tag_records)
        return formatted_tags

    def format_tags_records(self, dataset):
        """
        explanation
        iterate, put keys out front, containing an array (for table)
        """
        dict_of_tags = {}
        tagged_record = namedtuple('datatag', ['node', 'node_nanoid', 'property', 'property_nanoid', 'tag_value'])
        for row in dataset:
            tr = tagged_record(row[0], row[1], row[2], row[3], row[5])
            tag = row[4]

            if tag not in dict_of_tags:
                dict_of_tags[tag] = []
            dict_of_tags[tag].append(tr)

        # sort by node
        for tag in dict_of_tags:
            stuff = dict_of_tags[tag]
            sorted_stuff = sorted(stuff, key=lambda x: (x.node, x.property, x.tag_value))
            dict_of_tags[tag] = sorted_stuff
        return dict_of_tags

    def get_tag_keys(self, model=None):
        with self.driver.session() as session:
            current_app.logger.warn('have model {}'.format(model))
            tag_records = session.read_transaction(self._get_tags_from_db, model)
            formatted_tags = self.format_tag_keys(tag_records)
        return formatted_tags

    def format_tag_keys(self, tag_records):
        """
        explanation
        iterate, put keys out front, containing an array (for table)
        """
        tag_keys = []
        #tagged_record = namedtuple('datatag', ['node', 'node_nanoid', 'property', 'property_nanoid', 'tag_value'])
        for row in tag_records:
            tag_key = row[4]
            tag_value = row[5]

            if tag_key not in tag_keys:
                tag_keys.append(tag_key)

        # sort by node
        tag_keys.sort()
        return tag_keys    


    def get_dataset_tags(self, dataset=None, model=None):
        with self.driver.session() as session:
            current_app.logger.warn('have model {}'.format(model))
            tag_records = session.read_transaction(self._get_dataset_tags_from_db, dataset, model)
            formatted_tags = self.format_tags_records(tag_records)
        return formatted_tags


    @staticmethod
    def _get_dataset_tags_from_db(tx, dataset=None, model=None):
        result = []

        current_app.logger.warn('getting for tag {} in model {}'.format(dataset, model))

        query_ = """
                MATCH (n:node)-[:has_property]->(p:property)-[:has_tag]->(t:tag)
                WHERE toLower(n.model) = toLower($model)
                AND   t.key = "submitter"
                AND   t.value = $dataset
                RETURN n.handle, n.nanoid, p.handle, p.nanoid, t.key, t.value;
                """

        db_records = None
        
        db_records = tx.run(query_, dataset=dataset, model=model)
        current_app.logger.warn(' point BB ... using model {}'.format(model))
        for record in db_records:
            result.append(record)

        return result

    def get_dataset_tag_choices(self):
        with self.driver.session() as session:
            tag_records = session.read_transaction(self._get_dataset_tag_choices_from_db)
            # formatted_tags = self.format_tags_records(tag_records)
        return tag_records

    @staticmethod
    def _get_dataset_tag_choices_from_db(tx, dataset=None, model=None):
        result = ()

        query_all_models_and_tag_choices = """
            MATCH (n:node)-[:has_property]->(p:property)-[:has_tag]->(t:tag)
            WHERE t.key = "submitter"
            RETURN distinct n.model, t.value
            ORDER by n.model ASC, t.value ASC
            """

        db_records = tx.run(query_all_models_and_tag_choices)

        # convert into nested tuple structure for optgroup selectfield
        # ('ICDC', (                <-  option
        #    ('NCATS', 'NCATS'),    <-  key, value pairs for selectfield
        #    ('Glioma', 'Glioma'),
        #    ('UBC01', 'UBC01')
        # )),

        # pt 1. organize for optgroup
        temp_results = {}
        for record in db_records:
            mdl = record[0]
            ky = record[1]
            #print(mdl)
            #print(ky)
            mdlky = mdl + "----" + ky
            if mdl not in temp_results:
                temp_results[mdl] = ()
            temp_results[mdl] += ((mdlky, ky),)

        # pt 2. casting from dict to tuple needed for optgroup
        for m in temp_results:
            result += (m, temp_results[m])

        print('')
        print((result,))
        return (result,)

    def get_submitter_tag_choices(self, model=None):
        with self.driver.session() as session:
            tag_records = session.read_transaction(self._get_submitter_tag_choices_from_db, model)
            # formatted_tags = self.format_tags_records(tag_records)
        return tag_records

    # note: there are a couple of approaches for getting tags from the database
    #       one could get them by starting at node, and then going to property
    #       but I'm now trying to also label the tag directly with {model:"ICDC"}
    #       so I can create "empty" datasets
    @staticmethod
    def _get_submitter_tag_choices_from_db(tx, model=None):
        result = []

        current_app.logger.warn('.yup... using model {}'.format(model))

        query_against_all_models = """
                MATCH (t:tag)
                WHERE t.key = 'submitter'
                RETURN DISTINCT t.model, t.value
                ORDER by t.model ASC, t.value ASC;
                """
        
        query_against_specific_model = """
                MATCH (t:tag)
                WHERE toLower(t.model) = toLower($model)
                AND   t.key = 'submitter'
                RETURN DISTINCT t.model, t.value
                ORDER by t.model ASC, t.value ASC;
                """

        db_records = None
        if model is None:
            db_records = tx.run(query_against_all_models,)
            current_app.logger.warn('.point 22 ... using model {}'.format(model))
        else:
            db_records = tx.run(query_against_specific_model, model=model)
            current_app.logger.warn('.point 23 ... using model {}'.format(model))
        
        # convert into nested tuple structure for optgroup selectfield
        # ('ICDC', (                <-  option
        #    ('NCATS', 'NCATS'),    <-  key, value pairs for selectfield
        #    ('Glioma', 'Glioma'),
        #    ('UBC01', 'UBC01')
        # )),

        # pt 1. organize for optgroup
        temp_results = {}
        for record in db_records:
            mdl = record[0]
            ky = record[1]
            #print(mdl)
            #print(ky)
            mdlky = mdl + "----" + ky
            if mdl not in temp_results:
                temp_results[mdl] = ()
            temp_results[mdl] += ((mdlky, ky),)

        # pt 2. casting from dict to tuple needed for optgroup
        for m in temp_results:
            result += (m, temp_results[m])

        print('')
        print((result,))
        return (result,)

        return result
