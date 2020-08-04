import os
import pprint
import json
from flask import url_for
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
        result = tx.run("MATCH (n:node) RETURN DISTINCT n.model as model")
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

    # ########################################################################################### #
    @staticmethod
    def _get_node_by_id_query(tx, nid, model=None):
        
        # // idea: n3 -> n1 --> n2
        result = {}
        query = ""

        if model is not None:
            query = """
            MATCH (n1:node)
            WHERE n1.nanoid6 = $nid
            WHERE n1.model = $model
            OPTIONAL MATCH (n1)<-[:has_src]-(r12:relationship)-[:has_dst]->(n2:node)
            OPTIONAL MATCH (n3)<-[:has_src]-(r31:relationship)-[:has_dst]->(n1:node)
            OPTIONAL MATCH (n1)-[:has_property]->(p1:property)
            OPTIONAL MATCH (n1)-[:has_concept]->(c1:concept)
            OPTIONAL MATCH (ct:term)-[:represents]->(c1)
            OPTIONAL MATCH (ct)-[:has_origin]->(o:origin)
            RETURN DISTINCT n1.nanoid6 as n1_id,
                        n1.handle as n1_handle,
                        n1.model as n1_model,
                        r12.nanoid6 as r12_id,
                        r12.handle as r12_handle,
                        n2.nanoid6 as n2_id,
                        n2.handle  as n2_handle,
                        n2.model   as n2_model,
                        r31.nanoid6    as r31_id,
                        r31.handle as r31_handle,
                        n3.nanoid6 as n3_id,
                        n3.handle  as n3_handle,
                        n3.model   as n3_model,
                        p1.nanoid6 as p1_id,
                        p1.handle  as p1_handle,
                        p1.value_domain as p1_valuedomain,
                        p1.model as p1_model
                        """
        else:
            query = """
            MATCH (n1:node)
            WHERE n1.nanoid6 = $nid
            OPTIONAL MATCH (n1)<-[:has_src]-(r12:relationship)-[:has_dst]->(n2:node)
            OPTIONAL MATCH (n3)<-[:has_src]-(r31:relationship)-[:has_dst]->(n1:node)
            OPTIONAL MATCH (n1)-[:has_property]->(p1:property)
            OPTIONAL MATCH (n1)-[:has_concept]->(c1:concept)
            OPTIONAL MATCH (ct:term)-[:represents]->(c1)
            OPTIONAL MATCH (ct)-[:has_origin]->(o:origin)
            RETURN DISTINCT n1.nanoid6 as n1_id,
                        n1.handle as n1_handle,
                        n1.model as n1_model,
                        r12.nanoid6 as r12_id,
                        r12.handle as r12_handle,
                        n2.nanoid6 as n2_id,
                        n2.handle  as n2_handle,
                        n2.model   as n2_model,
                        r31.nanoid6    as r31_id,
                        r31.handle as r31_handle,
                        n3.nanoid6 as n3_id,
                        n3.handle  as n3_handle,
                        n3.model   as n3_model,
                        p1.nanoid6 as p1_id,
                        p1.handle  as p1_handle,
                        p1.value_domain as p1_valuedomain,
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
                pprint.pprint(from_node_)
                for other_node in result["has_relationship_from_nodes"]:
                    other_node_ = json.dumps(other_node, sort_keys=True)
                    pprint.pprint(other_node_)
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
                pass

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

    @staticmethod
    def _get_list_of_nodes_query(tx, model=None):
        result = []
        # todo: add version controls
        # swap handle to property.handle (vs.handle is null)
        if model is None:
            answers = tx.run(
                "MATCH (n:node) RETURN DISTINCT n.nanoid6 as id, n.handle as handle"
            )
        else:
            answers = tx.run(
                """
                MATCH (n:node) 
                WHERE n.model = $model 
                RETURN DISTINCT n.nanoid6 as id, n.handle as handle
                """, model=model,
            )

        for record in answers:
            row = {record["id"]: record["handle"]}
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

    # ############################################################################################### #
    def get_query_for_valueset_by_id(self, model=None):
        querystring = ""

        # todo: add version controls
        if model is None:
            querystring = """
            MATCH (vs:value_set)
            WHERE vs.nanoid6 = $vsid
            MATCH (p:property)-[:has_value_set]->(vs)
            OPTIONAL MATCH (p)-[:has_concept]->(cp:concept)
            OPTIONAL MATCH (ct:term)-[:represents]->(cp)
            OPTIONAL MATCH (vs)-[:has_term]->(t:term)
            OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
            OPTIONAL MATCH (vs)-[:has_origin]->(vso:origin)
            RETURN DISTINCT
                p.nanoid6 as property_id,
                p.handle as property_handle,
                p.model as property_model,
                vs.nanoid6 as vs_id,
                vs.url as vs_url,
                vs.handle as vs_handle,
                t.nanoid6 as term_id,
                t.value as term_value
            """
        else:
            querystring = """
            MATCH (vs:value_set)
            WHERE vs.nanoid6 = $vsid
            MATCH (p:property)-[:has_value_set]->(vs)
            WHERE toLower(p.model) = toLower($model)
            OPTIONAL MATCH (p)-[:has_concept]->(cp:concept)
            OPTIONAL MATCH (ct:term)-[:represents]->(cp)
            OPTIONAL MATCH (vs)-[:has_term]->(t:term)
            OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
            OPTIONAL MATCH (vs)-[:has_origin]->(vso:origin)
            RETURN DISTINCT
                p.nanoid6 as property_id,
                p.handle as property_handle,
                p.model as property_model,
                vs.nanoid6 as vs_id,
                vs.url as vs_url,
                vs.handle as vs_handle,
                t.nanoid6 as term_id,
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
                    "link": url_for('main.valuesets', id=record["vs_id"])
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
        # todo: add version controls
        if model is None:
            return """MATCH (vs:value_set)<-[:has_value_set]-(p:property)
                      RETURN DISTINCT vs.nanoid6 as id, p.handle as handle"""
        else:
            return """MATCH (vs:value_set)<-[:has_value_set]-(p:property) 
                      WHERE toLower(p.model) = toLower($model)
                      RETURN DISTINCT vs.nanoid6 as id, p.handle as handle"""

    def get_list_of_valuesets(self, model=None):
        with self.driver.session() as session:
            query = self.get_query_for_list_of_valuesets(model)
            list_o_dicts = session.read_transaction(self._do_query_for_list_of_valuesets, query, model)
        return list_o_dicts

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _get_term_by_id_query(tx, tid):
        result = {}
        answer = tx.run(
            "MATCH (t:term) "
            "WHERE t.nanoid6 = $tid "
            "OPTIONAL MATCH (t)-[:has_origin]->(to:origin) "
            "RETURN DISTINCT "
            "    t.nanoid6 as id, "
            "    t.value as value,"
            "    t.desc as desc,"
            "    t.origin_definition as origin_definition,"
            "    t.origin_id as origin_id,"
            "    to.nanoid6 as originid,"
            "    to.name as originname ",
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

    def get_term_by_id(self, tid):
        with self.driver.session() as session:
            term_ = session.read_transaction(self._get_term_by_id_query, tid)
        return term_

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _get_list_of_terms_query(tx, neo4jquery):
        result = []
        
        answers = tx.run(neo4jquery)
        
        for record in answers:
            row = {record["id"]: record["value"]}
            result.append(row)
        return result

    def get_query_for_list_of_terms(self):
        return """
                MATCH (t:term)
                MATCH (t)-[:has_origin]->(to:origin)
                MATCH (vs:value_set) -[:has_term]->(t)
                RETURN DISTINCT
                    t.nanoid6 as id, 
                    t.value as value,
                    to.name as origin
                """

    def get_list_of_terms(self):
        with self.driver.session() as session:
            query = self.get_query_for_list_of_terms()
            list_o_dicts = session.read_transaction(self._get_list_of_terms_query, query)
        return list_o_dicts

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _get_list_of_origins_query(tx):
        result = []
        # only get those terms associated with valuesets (some terms assoc w/ concepts)
        answers = tx.run(
            "MATCH (o:origin)"
            "RETURN DISTINCT"
            "    o.nanoid6 as id, "
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

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _get_list_of_properties_query(tx):
        result = []
        # only get those terms associated with valuesets (some terms assoc w/ concepts)
        answers = tx.run(
            """
            MATCH (p:property)
            OPTIONAL MATCH (p)-[:has_value_set]->(vs)
            OPTIONAL MATCH (vs)-[:has_term]->(t:term)
            RETURN DISTINCT
            p.nanoid6 as id,
            p.handle as handle,
            p.model as property_model,
            COUNT(DISTINCT(t.nanoid6))
                         """
        )
        for record in answers:
            row = {record["id"]: record["handle"]}
            result.append(row)
        return result

    def get_list_of_properties(self):
        with self.driver.session() as session:
            list_o_dicts = session.read_transaction(self._get_list_of_properties_query)
        return list_o_dicts

    @staticmethod
    def _get_property_by_id_query(tx, pid):
        result = {}
        _seen_terms = []

        # only get those terms associated with valuesets (some terms assoc w/ concepts)
        answers = tx.run(
            """
            MATCH (p:property)
            WHERE p.nanoid6 = $pid
            OPTIONAL MATCH (p)-[:has_value_set]->(vs)
            OPTIONAL MATCH (vs)-[:has_term]->(t:term)
            RETURN DISTINCT
            p.nanoid6 as id,
            p.handle as handle,
            p.model as model,
            p.value_domain as valuedomain,
            p.is_required as isrequired,
            vs.nanoid6 as valueset_id,
            t.nanoid6 as term_id,
            t.value as term_value,
            COUNT(DISTINCT(t.nanoid6))
            """,
            pid=pid,
        )

        for record in answers:

            # A. if result{} is empty (first time through) then initialize
            if not bool(result):
                result = {
                    "id": record["id"],
                    "handle": record["handle"],
                    "model": record["model"],
                    "value_domain": record["valuedomain"],
                    "is_required": record["isrequired"],
                    "type": "property",
                    "link": "/properties/" + record["id"],
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

    def get_property_by_id(self, pid):
        with self.driver.session() as session:
            property_ = session.read_transaction(self._get_property_by_id_query, pid)
        return property_
