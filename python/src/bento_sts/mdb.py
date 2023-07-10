import os
from flask import url_for, current_app
from bento_meta.mdb import SearchableMDB
from bento_meta.model import Model
from bento_meta.object_map import ObjectMap


plural = {
    "node": "nodes",
    "edge": "edges",
    "relationship": "relationships",
    "property": "properties",
    "tag": "tags",
    "origin": "origins",
    "predicate": "predicates",
    "value_set": "value_sets",
    "term": "terms",
    }

class mdb():
    """Read functionality for driving STS UI. Mixins mdb_update and mdb_tags
could be used here for write and tag functionality."""
    def __init__(self):
        self.mdb = SearchableMDB(current_app.config["NEO4J_MDB_URI"],
                       user=current_app.config["NEO4J_MDB_USER"],
                       password=current_app.config["NEO4J_MDB_PASS"])

    def close(self):
        self.mdb.close()

    def get_list_of_models(self):
        models = self.mdb.get_model_nodes()
        if models:
            return [x["m"] for x in models]
        else:
            return []

    """
    In [4]: m.get_model_by_name('ICDC')
    Out[4]: <bento_meta.model.Model at 0x110378450>
    """
    def get_model_by_name(self, name):
        ObjectMap.clear_cache()
        model = Model(name, self.mdb)
        model_node = self.mdb.get_model_nodes(model=name)
        # if you dont call dget, it wont be populated...
        model.dget()
        model.repository = model_node[0]["m"]["repository"]
        return model

    # ####################################################################### #
    # NODES
    # ####################################################################### #
    def get_node_by_id(self, nid, model=None):
        props_result = self.mdb.get_node_and_props_by_node_id(nid)
        edges_result = self.mdb.get_node_edges_by_node_id(nid)
        to_nodes = {}
        from_nodes = {}
        if not props_result and not edges_result:
            return {}
        result = {"id": nid,
                  "handle": props_result[0]["handle"],
                  "model": props_result[0]["model"],
                  "has_properties": [],
                  "has_relationship_to_nodes": [],
                  "has_relationship_from_nodes": []}
        if (props_result):
            for p in props_result[0]["props"]:
                result["has_properties"].append({
                    "id": p["nanoid"],
                    "handle": p["handle"],
                    "type": "property",
                    "link": url_for("main.entities", entities='properties',
                                    id=p["nanoid"]),
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
                    "link": url_for("main.entities", entities='nodes',
                                    id=node["nanoid"]),
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

    # ----------------------------------------------------------------------- #

    def get_list_of_nodes(self, model=None):
        """
        In [3]: m.get_list_of_nodes()
        Out[3]:
        [{'yXWr0Y': 'study_site'},
         {'N0Qx7Z': 'off_study'},
         {'nUoHJH': 'diagnosis
        """
        result = self.mdb.get_nodes_by_model(model)
        if result:
            return [(x["nanoid"], x["handle"], x["model"]) for x in result]
        else:
            return []

    # ####################################################################### #
    # VALUESETS
    # ####################################################################### #

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
            "link": url_for("main.entities", entities='valuesets',
                            id=vs_result[0]["nanoid"]),
            "_for_propertyhandle": "_for_propertyhandle",  # kludge
            "_for_propertyid": "_for_propertyid"  # kludge
            }
        result["has_property"] = [{"id": x["nanoid"], "handle": x["handle"],
                                   "type": "property", "model": x["model"],
                                   "link": "/properties/{}".format(x["nanoid"])}
                                  for x in vs_result[0].props]
        result["has_terms"] = [{"id": x["nanoid"], "value": x["value"],
                                "type": "term",
                                "link":url_for('main.entities', entities='terms',
                                               id=x["nanoid"])}
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

    # ----------------------------------------------------------------------- #

    def get_list_of_valuesets(self, model=None):
        vs_result = self.mdb.get_valuesets_by_model(model)
        if not vs_result:
            return []
        # kludge assuming that there is only one property assoc with each
        # valueset:
        return [{"id": x["value_set"]["nanoid"],
                 "handle": x["props"][0]["handle"]}
                for x in vs_result]

    # ####################################################################### #
    # TERMS
    # ####################################################################### #
    def get_term_by_id(self, tid):
        t_result = self.mdb.get_term_by_id(tid)
        if not t_result:
            return {}
        result = t_result[0]["term"]
        result["id"] = result["nanoid"]
        del result["nanoid"]
        result["type"] = "term"
        result["link"] = url_for("main.entities", entities='terms',
                                 id=result["id"],
                                 _external=False)
        result["has_origin"] = {}
        origin = t_result[0]["origin"]
        if origin:
            origin["id"] = origin["nanoid"]
            origin["type"] = "origin"
            origin["link"] = "/origins/{}".format(origin["nanoid"])
            result["has_origin"] = origin
        return result

    # ======================================================================= #

    def get_list_of_terms(self, model=None):
        t_result = self.mdb.get_props_and_terms_by_model(model)
        result = []
        for p in t_result:
            result.extend([{"id": x["nanoid"], "value": x["value"] if "value" in x else None,
                            "property": p["prop"]["handle"],
                            "model": p["prop"]["model"],
                            "propid": p["prop"]["nanoid"]}
                           for x in p["terms"]])
        return result

    # ####################################################################### #
    # ORIGINS
    # ####################################################################### #

    def get_list_of_origins(self, dummy=None):
        origins = self.mdb.get_origins()
        result = [{x["o"]["nanoid"]:x["o"]["name"]}
                  for x in origins]
        if result:
            return result
        else:
            return []

    def get_origin_by_id(self, oid):
        result = self.mdb.get_origin_by_id(oid)
        return result

    # ####################################################################### #
    # PROPERTIES
    # ####################################################################### #

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
            "model": pr["model"],
            "prop": pr["prop"],
            "type": "property",
            "link": "/properties/{}".format(pr["id"]),
            "_for_nodehandle": pr["node"]["handle"],
            "_for_nodeid": pr["node"]["nanoid"]
            }
        if pr["value_set"]:
            result["has_valueset"] = {
                "id": pr["value_set"]["nanoid"],
                "type": "valueset",
                "link": url_for("main.entities", entities='valuesets',
                                id=pr["value_set"]["nanoid"])
                }
        if pr["terms"]:
            result["has_terms"] = [{"id": t["nanoid"], "value": t["value"],
                                    "type": "term",
                                    "link": url_for("main.entities",
                                                    entities='terms',
                                                    id=t["nanoid"])}
                                   for t in pr["terms"]]
        return result

    # TAGS
    
    def get_tagged_entities(self, tag_key, tag_value=None, model=None):
        ents_by_tag = self.mdb.get_entities_by_tag(tag_key, tag_value, model)
        for i in range(0, len(ents_by_tag)):
            ents_by_tag[i]['plural'] = plural[ents_by_tag[i]['entity']]
        return ents_by_tag

    def get_tags_and_values(self):
        tags = self.mdb.get_tags_and_values()
        return tags

    # SEARCH

    def search_entity_handles(self, qstring):
        return self.mdb.search_entity_handles(qstring)

    def search_terms(self, qstring, search_values=True,
                     search_definitions=True):
        return self.mdb.search_terms(qstring, search_values=search_values,
                                     search_definitions=search_definitions)
