import os
import pprint
import json
from flask import url_for
from neo4j import GraphDatabase
from bento_meta.model import Model
from bento_meta.objects import Node, Term, Property, ValueSet
from bento_meta.object_map import ObjectMap

class mdb:
    def __init__(self):
        self.uri = os.environ.get("NEO4J_MDB_URI")
        self.user = os.environ.get("NEO4J_MDB_USER")
        self.password = os.environ.get("NEO4J_MDB_PASS")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self._model_handles = []
        self.models = {}
        for cls in [Node, Term, Property, ValueSet]:
            cls.drv = self.driver

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

    def get_list_of_models(self,force=False):
        if (force or self._model_handles == []):
            with self.driver.session() as session:
                models = session.read_transaction(self._get_models_query)
            return models
        else:
            return self._model_handles

    """
    In [4]: m.get_model_by_name('ICDC')
    Out[4]: <bento_meta.model.Model at 0x110378450>
    """

    def get_model_by_name(self, name, force=False):
        if (not self.models[name] or force):
            ObjectMap.clear_cache()
            model = Model(name, self.driver)
            model.dget()
            self.models[name] = model
        return self.models[name]

    def get_node_by_id(self, nid, model_name = None):
        return Node.get_by_id(nid)

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

    def get_list_of_nodes(self, model_name):
        """
        In [3]: m.get_list_of_nodes()
        Out[3]:
        [{'yXWr0Y': 'study_site'},
         {'N0Qx7Z': 'off_study'},
         {'nUoHJH': 'diagnosis'}
        """
        model = self.get_model_by_name(model_name)
        if not model:
            return
        else:
            return [ { model.nodes[k].id : model.nodes[k].handle } for k in model.nodes ]


    def update_node_by_id(self, nid, nhandle):
        return self.get_node_by_id(nid).dput()

    def get_valueset_by_id(self, vsid, model_name):
        return ValueSet.get_by_id(vsid)

    def get_list_of_valuesets(self, model_name=None):
        which_models = []
        value_sets = []
        if model_name is None:
            which_models = self.get_list_of_models()
        else:
            which_models.append(model_name)
        for m in which_models:
            for p in self.get_model_by_name(m):
                if p.value_set:
                    value_sets.append(p.value_set)
        return value_sets

    def get_term_by_id(self, tid):
        return Term.get_by_id(tid)

    def get_list_of_terms(self, model=None):
        which_models = []
        terms = []
        if model_name is None:
            which_models = self.get_list_of_models()
        else:
            which_models.append(model_name)
        for m in which_models:
            for mm in self.get_model_by_name(m):
                for p in mm.props.values:
                    terms.extend(p.terms)
        return terms

    def update_term_by_id(self, tid, tvalue):
        term = Term.get_by_id(tid)
        if term:
            term.dput()
            return term
        else:
            return

    # terms: use model. You can add a term directly to a property, and the
    # valueset will be managed under the hood.
    # prop.term["newterm"] = Term({ "handle":"newterm", "id":"Agd443" })

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
        return term_


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
        return term_


    @staticmethod
    def _get_list_of_origins_query(tx):
        result = []
        answers = tx.run(
            "MATCH (o:origin)"
            "RETURN DISTINCT"
            "    o.nanoid as id, "
            "    o.name as name "
        )
        for record in answers:
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


    def get_list_of_properties(self, model=None):
        which_models = []
        props = []
        if model_name is None:
            which_models = self.get_list_of_models()
        else:
            which_models.append(model_name)
        for m in which_models:
            for mm in self.get_model_by_name(m):
                props.extend(mm.props.values())
        return props
        
    def get_property_by_id(self, pid, model=None):
        return Property.get_by_id(pid)
    
