import os
import pprint
from collections import namedtuple
from flask import url_for, current_app
from bento_meta.mdb import MDB
from bento_meta.model import Model
from bento_meta.object_map import ObjectMap


class mdb:
    def __init__(self):
        self.mdb = MDB(os.environ.get("NEO4J_MDB_URI"),
                       user=os.environ.get("NEO4J_MDB_USER"),
                       password=os.environ.get("NEO4J_MDB_PASS"))

    def close(self):
        self.mdb.close()

    def get_list_of_models(self):
        return self.mdb.get_model_handles()

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
    def get_node_by_id(self, nid, model=None):
        props_result = self.mdb.get_node_and_props_by_node_id(nid)
        edges_result = self.mdb.get_node_edges_by_node_id(nid)
        result = {"id": nid, "has_properties": [],
                  "has_relationship_to_nodes": [],
                  "has_reationship_from_nodes": []}
        to_nodes = {}
        from_nodes = {}
        if not props_result and not edges_result:
            return {}
        if (props_result):
            for p in props_result[0]:
                result["has_properties"].append({
                    "id": p["nanoid"],
                    "handle": p["handle"],
                    "type": "property",
                    "link": url_for("main.properties", id=p["nanoid"]),
                    "value_domain": p["value_domain"]
                    })
        if (edges_result):
            for e in edges_result:
                node = e["far_node"]
                rln = e["rln"]
                add_to = None
                if e["far_type"] == "has_src":
                    add_to = from_nodes
                elif e["far_type"] == "has_dst":
                    add_to = to_nodes
                else:
                    RuntimeError("What?")
                add_to[node["nanoid"]] = {
                    "id": node["nanoid"],
                    "handle": node["handle"],
                    "link": url_for("main.nodes", id=node["nanoid"]),
                    "type": "node",
                    "relationship": {
                        "id": rln["nanoid"],
                        "handle": rln["handle"],
                        "link": "/relationships/{}".format(rln["nanoid"]),
                        "type": "relationship"
                        }
                    }
            result["has_relationship_to_nodes"].extend(to_nodes.values())
            result["has_relationship_from_nodes"].extend(from_nodes.values())
        return result

    # ------------------------------------------------------------------------- #

    def get_list_of_nodes(self, model=None):
        """
        In [3]: m.get_list_of_nodes()
        Out[3]:
        [{'yXWr0Y': 'study_site'},
         {'N0Qx7Z': 'off_study'},
         {'nUoHJH': 'diagnosis
        """
        result = self.mdb.get_nodes_by_model(model)
        return [(x["nanoid"], x["handle"], x["model"]) for x in result]

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

    
    # ------------------------------------------------------------------------- #

    @staticmethod
    def _do_deprecate_node(tx, neo4jquery, nid):
        print("deprecating node {}".format(nid))
        result = []

        answers = tx.run(neo4jquery, nid=nid)

        for record in answers:
            result.append(record)
        return result

    def get_query_to_deprecate_node(self):
        return '''
                MATCH (n:node)
                WHERE n.nanoid = $nid and n._to IS NULL
                SET n._to = ( n._from + 1 )
                RETURN id(n);
                '''

    def deprecate_node(self, nid):
        with self.driver.session() as session:
            query = self.get_query_to_deprecate_node()
            node_ = session.write_transaction(self._do_deprecate_node, query, nid)
            # TODO update elasticsearch, remove old node
        return node_

    # ############################################################################################### #
    # VALUESETS
    # ############################################################################################### #

    def get_valueset_by_id(self, vsid, model=None):
        vs_result = self.mdb.get_valueset_by_id(vsid)
        if not vs_result:
            return {}
        result = {
            "id": vs_result[0]["nanoid"],
            "handle": vs_result[0]["handle"],
            "model": model,  # kludge
            "url": vs_result[0]["url"],
            "desc": vs_result[0]["desc"],
            "type": "valueset",
            "link": url_for("main.valuesets", id=vs_result[0]["nanoid"]),
            "_for_propertyhandle": "_for_propertyhandle",  # kludge
            "_for_propertyid": "_for_propertyid"  # kludge
            }
        result["has_property"] = [{"id": x["nanoid"], "handle": x["handle"],
                                   "type": "property", "model": x["model"],
                                   "link": "/properties/{}" .format(x["nanoid"])}
                                  for x in vs_result[0].props]
        result["has_terms"] = [{"id": x["nanoid"], "value": x["value"],
                                "type": "term",
                                "link":url_for('main_terms', id=x["nanoid"])}
                               for x in vs_result[0].terms]
        if model:
            result["has_property"] = [x for x in result["has_property"]
                                      if x["model"] == model]
        # kludge - original assumption is that a valueset has only one
        # associated property, but this is not necessarily true.
        if result["has_property"]:
            result["_for_propertyhandle"] = result["has_property"][0]["handle"]
            result["_for_propertyid"] = result["has_property"][0]["nanoid"]
        return result
    
    # ------------------------------------------------------------------------- #

    def get_list_of_valuesets(self, model=None):
        vs_result = self.mdb.get_valuesets_by_model(model)
        if not vs_result:
            return []
        # kludge assuming that there is only one property assoc with each
        # valueset:
        return [{"id": x["value_set"]["nanoid"],
                 "handle": x["props"][0]["handle"]}
                for x in vs_result]
    
    # ############################################################################################### #
    # TERMS
    # ############################################################################################### #
    def get_term_by_id(self, tid):
        t_result = self.mdb.get_term_by_id(tid)
        if not t_result:
            return None
        result = t_result[0]["term"]
        result["id"] = result["nanoid"]
        del result["nanoid"]
        result["type"] = "term"
        result["link"] = url_for("main.terms", id=result["id"],
                                 _external=False)
        result["has_origin"] = {}
        origin = t_result[0]["origin"]
        if origin:
            origin["id"] = origin["nanoid"]
            origin["type"] = "origin"
            origin["link"] = "/origins/{}".format(origin["nanoid"])
            result["has_origin"] = origin
        return result
    
    # ========================================================================= #

    def get_list_of_terms(self, model=None):
        t_result = self.mdb.get_prop_terms_by_model(model)
        result = []
        for p in t_result:
            result.extend([(x["nanoid"], x["value"],
                            p["prop"]["handle"], p["prop"]["model"],
                            p["prop"]["nanoid"]) for x in p["terms"]])
        return result.sort(key=lambda x: (x[3], x[2], x[1]))
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

    def get_list_of_origins(self):
        origins = self.mdb.get_origins()
        for o in origins:
            o["id"] = o["nanoid"]
        return origins
    
    # ############################################################################################### #
    # PROPERTIES
    # ############################################################################################### #

    def get_list_of_properties(self, model=None):
        np_result = self.mdb.get_nodes_and_props_by_model(model)
        if not np_result:
            return []
        result = []
        for np in np_result:
            result.extend([(p["nanoid"], p["handle"],
                            np["model"], np["handle"], np["id"])
                           for p in np["props"]])
        return result

    def get_property_by_id(self, pid, model=None):
        p_result = self.mdb.get_prop_node_and_domain_by_prop_id(pid)
        if not p_result:
            return {}
        pr = p_result[0]
        result = {
            "id": pr["id"],
            "handle": pr["handle"],
            "model": pr["model"],
            "value_domain": pr["value_domain"],
            "is_required": pr["prop"].get("is_required"),
            "type": "property",
            "link": "/properties/{}".format(pr["id"]),
            "_for_nodehandle": pr["node"]["handle"],
            "_for_nodeid": pr["node"]["nanoid"]
            }
        if pr["value_set"]:
            result["has_valueset"] = {
                "id": pr["value_set"]["nanoid"],
                "type": "valueset",
                "link": url_for("main.valuesets", id=pr["value_set"]["nanoid"])
                }
        if pr["terms"]:
            result["has_terms"] = [{"id": t["nanoid"], "value": t["value"],
                                    "type": "term",
                                    "link": url_for("main.terms",
                                                    id=t["nanoid"])}
                                   for t in pr["terms"]]
        return result

            
        # ======================================================================= #

    @staticmethod
    def _do_update_property(tx, neo4jquery, pid, phandle):
        print("working with pid {} for {}".format(pid, phandle))
        result = []

        answers = tx.run(neo4jquery, pid=pid, phandle=phandle)

        for record in answers:
            # row = {record["id(t2)"]: record["handle"]}
            result.append(record)
        return result

    def get_query_to_update_property(self):
        return '''
                MATCH (p1:property)
                WHERE p1.nanoid = $pid AND p1._to IS NULL
                CALL apoc.refactor.cloneNodesWithRelationships([p1])
                YIELD input, output
                MATCH (p2:property)
                where p2.nanoid = $pid and p2._to IS NULL and id(p1) <> id (p2)
                SET p1._to = ( p1._from + 1 ), p2._from = (p1._from + 1), p2.handle = $phandle
                RETURN id(p2)
                '''

    def update_property_by_id(self, pid, phandle):
        with self.driver.session() as session:
            query = self.get_query_to_update_property()
            property_ = session.write_transaction(self._do_update_property, query, pid, phandle)
            # TODO update elasticsearch, remove old term and add new term
        return property_

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _do_create_property(tx, neo4jquery, phandle):
        print("working with for {}".format(phandle))
        result = []

        answers = tx.run(neo4jquery, phandle=phandle)

        for record in answers:
            result.append(record)
        return result

    def get_query_to_create_property(self):
        return '''
                MATCH (p1:property)
                WHERE p1.handle = $phandle and p1._to IS NULL
                SET p1._to = ( p1._from + 1 ), p2._from = (p1._from + 1), p2.handle = $phandle
                RETURN id(p2);
                '''

    def create_property(self, phandle):
        with self.driver.session() as session:
            query = self.get_query_to_create_property()
            property_ = session.write_transaction(self._do_create_property, query, phandle)
            # TODO update elasticsearch add new term
        return property_

    # ------------------------------------------------------------------------- #

    @staticmethod
    def _do_deprecate_property(tx, neo4jquery, pid):
        print("deprecating property {}".format(pid))
        result = []

        answers = tx.run(neo4jquery, pid=pid)

        for record in answers:
            result.append(record)
        return result

    def get_query_to_deprecate_property(self):
        return '''
                MATCH (p:property)
                WHERE p.nanoid = $pid and p._to IS NULL
                SET p._to = ( p._from + 1 )
                RETURN id(p);
                '''

    def deprecate_property(self, pid):
        with self.driver.session() as session:
            query = self.get_query_to_deprecate_property()
            property_ = session.write_transaction(self._do_deprecate_property, query, pid)
            # TODO update elasticsearch, remove old term
        return property_




    # ############################################################################################### #
    # DATA SUBSETS / TAGS
    # ############################################################################################### #

    @staticmethod
    def _get_tags_from_db(tx, model=None):
        result = []

        current_app.logger.warn('yup... using model {}'.format(model))

        query_against_all_models = """
                MATCH (n:node) -[:has_property]->(p:property)-[:has_tag]->(t:tag)
                WHERE n._to IS NULL 
                AND   p._to IS NULL
                RETURN n.handle, n.nanoid, p.handle, p.nanoid, t.key, t.value;
                """
        query_against_specific_model = """
                MATCH (n:node) -[:has_property]->(p:property)-[:has_tag]->(t:tag)
                WHERE n._to IS NULL 
                AND   p._to IS NULL
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

        dataset_query_ = """
                MATCH (n:node)-[np:has_property]->(p:property)-[:has_tag]->(t:tag)
                WHERE toLower(n.model) = toLower($model)
                AND   t.key = "submitter"
                AND   t.value = $dataset
                AND   n._to IS NULL
                AND   p._to IS NULL
                MATCH (n)-[z:in_dataset { dataset: $dataset } ]->(p)
                RETURN n.handle, n.nanoid, p.handle, p.nanoid, t.key, t.value;
                """

        all_query_ = """
                MATCH (n:node)-[np:has_property]->(p:property)
                WHERE toLower(n.model) = toLower($model)
                AND   n._to IS NULL
                AND   p._to IS NULL
                RETURN n.handle, n.nanoid, p.handle, p.nanoid, n.ONLYthisANDnothingMORE, n.QUOTHtheRAVENnevermore; 
                """


        db_records = None

        if (dataset == 'all') or dataset is None:
            db_records = tx.run(all_query_, dataset=dataset, model=model)
            current_app.logger.warn(' getting entire model {}'.format(model))
            for record in db_records:
                result.append(record)

        else:
            db_records = tx.run(dataset_query_, dataset=dataset, model=model)
            current_app.logger.warn(' getting all tags w/ dataset ... using model {}'.format(model))
            for record in db_records:
                result.append(record)





        return result



    def get_dataset(self, dataset=None, model=None):
        with self.driver.session() as session:
            current_app.logger.warn('have model {}'.format(model))
            tag_records = session.read_transaction(self._get_dataset_from_db, dataset, model)
        return tag_records
            #formatted_tags = self.format_tags_records(tag_records)
        #return formatted_tags


    @staticmethod
    def _get_dataset_from_db(tx, dataset=None, model=None):
        result = []

        current_app.logger.warn('getting for tag {} in model {}'.format(dataset, model))

        dataset_query_ = """
                MATCH (n:node)-[np:has_property]->(p:property)-[:has_tag]->(t:tag)
                WHERE toLower(n.model) = toLower($model)
                AND   t.key = "submitter"
                AND   t.value = $dataset
                AND   n._to IS NULL
                AND   p._to IS NULL
                MATCH (n)-[z:in_dataset { dataset: $dataset } ]->(p)
                OPTIONAL MATCH (p)-[:has_value_set]->(vs:value_set)
                RETURN n.handle, n.nanoid, p.handle, p.nanoid, t.key, t.value, p.value_domain, vs.nanoid, p.required, p.units, p.description, p.instructions, p.internal_comments, p.example ;
                """

        all_query_ = """
                MATCH (n:node)-[np:has_property]->(p:property)
                WHERE toLower(n.model) = toLower($model)
                AND   n._to IS NULL
                AND   p._to IS NULL
                OPTIONAL MATCH (p)-[:has_value_set]->(vs:value_set)
                RETURN n.handle, n.nanoid, p.handle, p.nanoid, n.ONLYthisANDnothingMORE, n.QUOTHtheRAVENnevermore, p.value_domain, vs.nanoid, p.required, p.units, p.description, p.instructions, p.internal_comments, p.example; 
                """


        db_records = None

        if (dataset == 'all') or dataset is None:
            db_records = tx.run(all_query_, dataset=dataset, model=model)
            current_app.logger.warn(' getting entire model {}'.format(model))
            for record in db_records:
                _entry = []
                for part in record:
                    _entry.append(part)
                #result.append(record)
                result.append(_entry)

        else:
            db_records = tx.run(dataset_query_, dataset=dataset, model=model)
            current_app.logger.warn(' getting all tags w/ dataset ... using model {}'.format(model))
            for record in db_records:
                #result.append(record)
                _entry = []
                for part in record:
                    _entry.append(part)
                result.append(_entry)

        return result



    def get_dataset_tag_choices(self):
        with self.driver.session() as session:
            tag_records = session.read_transaction(self._get_dataset_tag_choices_from_db)
            # formatted_tags = self.format_tags_records(tag_records)
        return tag_records

    @staticmethod
    def _get_dataset_tag_choices_from_db(tx, dataset=None, model=None):
        result = ()

        OLD_query_all_models_and_tag_choices = """
            MATCH (n:node)-[np:has_property]->(p:property)-[:has_tag]->(t:tag)
            WHERE t.key = "submitter"
            AND   n._to IS NULL
            AND   p._to IS NULL
            AND EXISTS (np.dataset)
            RETURN distinct n.model, t.value
            ORDER by n.model ASC, t.value ASC
            """

        NEW_query_all_models_and_tag_choices = """
            MATCH (t:tag)
            WHERE t.key = "submitter"
            RETURN distinct t.model, t.value
            ORDER by t.model ASC, t.value ASC
            """

        query_all_models_and_tag_choices = NEW_query_all_models_and_tag_choices

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
            #print(' model is {}'.format(mdl))
            #print(' key is {}'.format(ky))
            mdlky = mdl + "----" + ky
            if mdl not in temp_results:
                temp_results[mdl] = ()
            arglbargl = temp_results[mdl]
            funkmeister = (mdlky, ky)
            temp_results[mdl] = arglbargl + (funkmeister,)

        # pt 2. casting from dict to tuple needed for optgroup
        for m in temp_results:
            flashmasterj = (m, temp_results[m])
            result = result + (flashmasterj,)

        #print('')
        #print('result is {}'.format(result))
        return result

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
        result = ()

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
            #print(' model is {}'.format(mdl))
            #print(' key is {}'.format(ky))
            mdlky = mdl + "----" + ky
            if mdl not in temp_results:
                temp_results[mdl] = ()
            arglbargl = temp_results[mdl]
            funkmeister = (mdlky, ky)
            temp_results[mdl] = arglbargl + (funkmeister,)

        # pt 2. casting from dict to tuple needed for optgroup
        for m in temp_results:
            flashmasterj = (m, temp_results[m])
            result = result + (flashmasterj,)

        #print('')
        #print(result)
        return result

    def create_submitter_tag_for_model(self, model=None, tag=None):
        with self.driver.session() as session:
            if (model is not None) and (tag is not None):
                tag_records = session.read_transaction(self._create_submitter_tag_for_model, model, tag)
                # formatted_tags = self.format_tags_records(tag_records)
        return tag_records


    @staticmethod
    def _create_submitter_tag_for_model(tx, model=None, tag=None):
        result = None

        current_app.logger.warn('getting for tag {} in model {}'.format(model, tag))

        create_tag_query_ = """
                MERGE (t:tag {model:$model, key:"submitter", value:$tag})
                RETURN id(t);
                """

        db_records = tx.run(create_tag_query_, model=model, tag=tag)
        current_app.logger.warn('..point BB ... using model {}'.format(model))
        result = db_records.single()[0]

        return result



    def add_submitter_tag_for_model_prop(self, model=None, nodenanoid=None, propnanoid=None, tag=None):
        with self.driver.session() as session:
            if (model is not None) and (tag is not None) and (nodenanoid is not None) and (propnanoid is not None):
                tag_records = session.read_transaction(self._add_submitter_tag_for_model, model, nodenanoid, propnanoid, tag)
                tag_records = session.read_transaction(self._add_submitter_tag_for_prop, model, nodenanoid, propnanoid, tag)
                # formatted_tags = self.format_tags_records(tag_records)
        return tag_records


    @staticmethod
    def _add_submitter_tag_for_model(tx, model=None, nodenanoid=None, propnanoid=None, tag=None):
        result = None

        current_app.logger.warn('ADD tag {} for node {} prop {} in model {}'.format(model, nodenanoid, propnanoid, tag))

        add_tag_query_ = """
                MATCH (n:node { model:$model, nanoid:$nodenanoid })-[np:has_property]->(p:property { nanoid:$propnanoid, model:$model })
                WHERE n._to IS NULL AND p._to IS NULL
                MATCH (t:tag {key:'submitter', model:$model, value:$tag})
                MERGE (p)-[r:has_tag]->(t);
                """
                #MERGE (p)-[r:has_tag]->(t);

        db_records = tx.run(add_tag_query_, model=model, nodenanoid=nodenanoid, propnanoid=propnanoid, tag=tag)
        current_app.logger.warn('..adding tag ... to model {}'.format(model))
        #result = db_records.single()[0]

        return        

    @staticmethod
    def _add_submitter_tag_for_prop(tx, model=None, nodenanoid=None, propnanoid=None, tag=None):
        result = None

        current_app.logger.warn('ADD tag {} for node {} prop {} in model {}'.format(model, nodenanoid, propnanoid, tag))

        add_tag_query_ = """
                MATCH (n:node { model:$model, nanoid:$nodenanoid })-[np:has_property]->(p:property { nanoid:$propnanoid, model:$model })
                -[r:has_tag]->(t:tag {key:'submitter', model:$model, value:$tag})
                WHERE n._to IS NULL AND p._to IS NULL
                MERGE (n)-[z:in_dataset { dataset: $tag } ]->(p);
                """
                #MERGE (p)-[r:has_tag]->(t);

        db_records = tx.run(add_tag_query_, model=model, nodenanoid=nodenanoid, propnanoid=propnanoid, tag=tag)
        current_app.logger.warn('..adding tag ... to prop {}'.format(model))
        #result = db_records.single()[0]

        return   





    def remove_submitter_tag_for_model_prop(self, model=None, nodenanoid=None, propnanoid=None, tag=None):
        with self.driver.session() as session:
            if (model is not None) and (tag is not None) and (nodenanoid is not None) and (propnanoid is not None):
                tag_records = session.read_transaction(self._remove_submitter_tag_for_model_prop, model, nodenanoid, propnanoid, tag)
                # formatted_tags = self.format_tags_records(tag_records)
        return tag_records

    @staticmethod
    def _remove_submitter_tag_for_model_prop(tx, model=None, nodenanoid=None, propnanoid=None, tag=None):
        result = None

        current_app.logger.warn('REMOVING for tag {} for node {} prop {} in model {}'.format(model, nodenanoid, propnanoid, tag))

        count_nodetag_query_ = """
                MATCH (t:tag { value: $tag })<-[r:has_tag]-(p:property {nanoid: $propnanoid })<-[np:has_property]-(n:node)
                WHERE n._to IS NULL AND p._to IS NULL
                with p,count(n) as rels
                return rels;
                """

        db_records = tx.run(count_nodetag_query_, model=model, nodenanoid=nodenanoid, propnanoid=propnanoid, tag=tag)
        result = db_records.single()[0]
        current_app.logger.warn('..found {} counts - for removing tag from model'.format(result))

        ''' only remove p-n tag '''
        if result == 1:
            remove_both_query_ = """
                    MATCH (n:node { model:$model, nanoid:$nodenanoid })-[z:in_dataset { dataset: $tag } ]->(p:property { nanoid:$propnanoid, model:$model })-[r:has_tag]->(t:tag {key:'submitter', model:$model, value:$tag}) 
                    WHERE n._to IS NULL AND p._to IS NULL
                    DELETE r, z
                    """

            db_records = tx.run(remove_both_query_, model=model, nodenanoid=nodenanoid, propnanoid=propnanoid, tag=tag)
            current_app.logger.warn('..removing tag from model {}'.format(model))

        ''' only remove p-n tag '''
        if result > 1:
            remove_node_query_ = """
                    MATCH (n:node { model:$model, nanoid:$nodenanoid })-[z:in_dataset { dataset: $tag } ]->(p:property { nanoid:$propnanoid, model:$model })-[r:has_tag]->(t:tag {key:'submitter', model:$model, value:$tag}) 
                    WHERE n._to IS NULL AND p._to IS NULL
                    DELETE z
                    """

            db_records = tx.run(remove_node_query_, model=model, nodenanoid=nodenanoid, propnanoid=propnanoid, tag=tag)
            current_app.logger.warn('..removing tag from model {}'.format(model))

        return
