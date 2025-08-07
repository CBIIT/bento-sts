from __future__ import annotations

import functools

from bento_meta.mdb import SearchableMDB
from bento_meta.model import Model
from flask import url_for

plural = {
    "node": "nodes",
    "edge": "edges",
    "relationship": "relationships",
    "property": "properties",
    "tag": "tags",
    "origin": "origins",
    "concept": "concepts",
    "predicate": "predicates",
    "value_set": "value_sets",
    "term": "terms",
}


class mdb:
    """
    Read functionality for driving STS UI. Mixins mdb_update and mdb_tags
    could be used here for write and tag functionality.
    """

    mdb_ = None
    term_values = None

    def __init__(self, uri, user, pw):
        if mdb.mdb_ is None:
            mdb.mdb_ = SearchableMDB(uri, user, pw)

    def close(self):
        self.mdb.close()

    @property
    def mdb(self):
        return mdb.mdb_

    def get_with_statement(self, qry, parms):
        return self.mdb.get_with_statement(qry, parms)

    def get_list_of_models(self):
        models = self.mdb.get_model_nodes()
        ret = {}
        if models:
            for mdl in models:
                h = mdl["m"]["handle"]
                if ret.get(h):
                    ret[h]["version"].append(mdl["m"]["version"])
                else:
                    ret[h] = mdl["m"]
                    if not ret[h].get("name"):
                        ret[h]["name"] = ret[h]["handle"]
                    ret[h]["version"] = [mdl["m"]["version"]]
        return [x for x in ret.values()]

    def get_model_by_name(self, name):
        model_nodes = self.mdb.get_model_nodes(model=name)
        models = []
        for node in model_nodes:
            model = Model(handle=name)
            model.version = node["m"].get("version")
            model.repository = node["m"].get("repository")
            models.append(model)
        return models

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
        result = {
            "id": nid,
            "handle": props_result[0]["handle"],
            "model": props_result[0]["model"],
            "version": props_result[0].get("version"),
            "has_properties": [],
            "has_relationship_to_nodes": [],
            "has_relationship_from_nodes": [],
        }
        if props_result:
            for p in props_result[0]["props"]:
                result["has_properties"].append(
                    {
                        "id": p["nanoid"],
                        "handle": p["handle"],
                        "model": p["model"],
                        "version": p.get("version"),
                        "type": "property",
                        "link": url_for(
                            "main.entities",
                            entities="properties",
                            id=p["nanoid"],
                        ),
                        "value_domain": p["value_domain"],
                    },
                )
        if edges_result:
            for e in edges_result:
                node = e["far_node"]
                if node:
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
                        "model": node["model"],
                        "version": node.get("version"),
                        "link": url_for(
                            "main.entities",
                            entities="nodes",
                            id=node["nanoid"],
                        ),
                        "type": "node",
                        "relationship": {
                            "id": rln["nanoid"],
                            "handle": rln["handle"],
                            "model": rln["model"],
                            "version": rln.get("version"),
                            "link": "/relationships/{}".format(rln["nanoid"]),
                            "type": "relationship",
                        },
                    }
            result["has_relationship_to_nodes"].extend(to_nodes.values())
            result["has_relationship_from_nodes"].extend(from_nodes.values())
        return result

    # ----------------------------------------------------------------------- #

    def get_list_of_nodes(self, model=None, version=None):
        """
        In [3]: m.get_list_of_nodes()
        Out[3]:
        [{'yXWr0Y': 'study_site'},
         {'N0Qx7Z': 'off_study'},
         {'nUoHJH': 'diagnosis
        """
        if model == "ALL":
            model = None
            version = None
        elif version == "ALL":
            version = "*"
        result = self.mdb.get_nodes_by_model(model, version)
        if result:
            return [
                (x["nanoid"], x["handle"], x["model"], x["version"]) for x in result
            ]
        return []

    # ####################################################################### #
    # PROPERTIES
    # ####################################################################### #

    def get_list_of_properties(self, model=None, version=None):
        if model == "ALL":
            model = None
            version = None
        elif version == "ALL":
            version = "*"
        np_result = self.mdb.get_nodes_and_props_by_model(model, version)
        if not np_result:
            return []
        result = []
        for np in np_result:
            result.extend(
                [
                    {
                        "prop_id": p["nanoid"],
                        "prop_handle": p["handle"],
                        "node_model": np["model"],
                        "node_handle": np["handle"],
                        "node_id": np["id"],
                        "node_version": np.get("version"),
                    }
                    for p in np["props"]
                ],
            )
        return result

    def get_property_by_id(self, pid, model=None):
        p_result = self.get_with_statement(
            "match (p:property {nanoid:$pid})<-[:has_property]-(n:node) "
            "with p,n "
            "optional match (p)-[:has_concept]->(:concept)<-[:represents]-(a:term) "
            "optional match (p)-[:has_value_set]->(vs:value_set)-[:has_term]->(t:term) "
            "return p.nanoid as id, p.handle as handle, p.model as model, "
            "p.version as version, "
            "p.value_domain as value_domain, p as prop, n as node, "
            "  vs as value_set, collect(distinct a) as annots, collect(t) as terms",
            {"pid": pid},
        )
        if not p_result:
            return {}
        pr = p_result[0]
        pr["type"] = "property"
        pr["link"] = "/properties/{}".format(pr["id"])
        # pr["version"] = pr.get("version"),
        if pr["value_set"]:
            pr["has_valueset"] = {
                "id": pr["value_set"]["nanoid"],
                "type": "valueset",
                "link": url_for(
                    "main.entities",
                    entities="valuesets",
                    id=pr["value_set"]["nanoid"],
                ),
            }
        if pr["terms"]:
            pr["has_terms"] = [
                {
                    "id": t["nanoid"],
                    "value": t["value"],
                    "origin": t["origin_name"] if "origin_name" in t else None,
                    "type": "term",
                    "link": url_for("main.entities", entities="terms", id=t["nanoid"]),
                }
                for t in pr["terms"]
                if "nanoid" in t
            ]
        if pr["annots"]:
            pr["has_annots"] = [
                {
                    "id": t["nanoid"],
                    "value": t["value"],
                    "origin": t["origin_name"] if "origin_name" in t else None,
                    "type": "term",
                    "link": url_for("main.entities", entities="terms", id=t["nanoid"]),
                }
                for t in pr["annots"]
                if "nanoid" in t
            ]
        return pr

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
            "link": url_for(
                "main.entities",
                entities="valuesets",
                id=vs_result[0]["nanoid"],
            ),
            "_for_propertyhandle": "_for_propertyhandle",  # kludge
            "_for_propertyid": "_for_propertyid",  # kludge
        }
        result["has_property"] = [
            {
                "id": x["nanoid"],
                "handle": x["handle"],
                "type": "property",
                "model": x["model"],
                "link": "/properties/{}".format(x["nanoid"]),
            }
            for x in vs_result[0].props
        ]
        result["has_terms"] = [
            {
                "id": x["nanoid"],
                "value": x["value"],
                "origin": x["origin_name"] if "origin_name" in x else None,
                "type": "term",
                "link": url_for("main.entities", entities="terms", id=x["nanoid"]),
            }
            for x in vs_result[0].terms
        ]
        if model:
            result["has_property"] = [
                x for x in result["has_property"] if x["model"] == model
            ]
        # kludge - original assumption is that a valueset has only one
        # associated property, but this is not necessarily true.
        if result["has_property"]:
            result["_for_propertyhandle"] = result["has_property"][0]["handle"]
            result["_for_propertyid"] = result["has_property"][0]["nanoid"]
        return result

    # ----------------------------------------------------------------------- #

    def get_list_of_valuesets(self, model=None, version=None):
        vs_result = self.mdb.get_valuesets_by_model(model, version)
        if not vs_result:
            return []
        # kludge assuming that there is only one property assoc with each
        # valueset:
        return [
            {"id": x["value_set"]["nanoid"], "handle": x["props"][0]["handle"]}
            for x in vs_result
        ]

    # ####################################################################### #
    # TERMS
    # ####################################################################### #

    def get_term_batch_info(self, nbatches, start=0, ct=None):
        batches = []
        tabnames = []
        if not mdb.term_values:
            try:
                res = self.get_with_statement(
                    "match (t:term) with t.value as val return val order by val",
                    {},
                )
            except Exception as e:
                raise e
            mdb.term_values = [x["val"] for x in res]
        if ct is None:
            ct = len(self.term_values)
        bsize = ct // nbatches or ct
        for n in range(start, min(start + ct, len(self.term_values)), bsize):
            l = min(n + bsize - 1, len(self.term_values) - 1)
            batches.append(
                {
                    "first": n,
                    "first_term": self.term_values[n],
                    "last": l,
                    "last_term": self.term_values[l],
                },
            )

        # if n+bsize != start+ct:
        #     batches[-1]['last'] = start+ct-1
        #     batches[-1]['last_term'] = self.term_values[start+ct-1]

        for n in range(len(batches)):
            v1 = batches[n]["first_term"] or "___"
            v2 = batches[n]["last_term"] or "___"
            tabnames.append(f"{v1[0:3]}-{v2[0:3]}")

        return (batches, tabnames)

    @functools.lru_cache
    @staticmethod
    def get_term_batch(start, bsize):
        try:
            res = mdb.mdb_.get_with_statement(
                "match (t:term) with t order by t.value "
                "return t as term skip $start limit $bsize",
                {"start": start, "bsize": bsize},
            )
        except Exception as e:
            raise e
        return res

    def get_term_by_id(self, tid):
        t_result = self.get_with_statement(
            "match (t:term {nanoid:$id}) "
            "optional match (t)<-[:has_term]-(v:value_set)<-[:has_value_set]-(p:property) "
            "with t as term, t.origin_name as oname,  collect(p) as props "
            "optional match (o:origin) where o.name = oname "
            "return term, o as origin, props ",
            {"id": tid},
        )
        if not t_result:
            return {}
        result = t_result[0]
        result["props"] = sorted(
            result["props"],
            key=lambda x: (x["handle"], x["model"], x.get("version")),
        )
        s_result = self.get_with_statement(
            "match (t:term {nanoid:$id})-[:represents]->(c:concept)<-[:represents]-(s:term) "
            "optional match (g:tag {key:'mapping_source'})<-[:has_tag]-(c) "
            "return s.value as value, s.nanoid as id, s.origin_name as origin, collect(g.value) as sources",
            {"id": tid},
        )
        if s_result:
            result["synonyms"] = sorted(s_result, key=lambda x: x["value"])
        else:
            result["synonyms"] = None
        return result

    def get_list_of_terms(self, start=None, end=None):
        t_result = self.get_with_statement(
            "match (t:term)<-[:has_term]-(:value_set) "
            "with distinct t as t "
            "return t.value as value, t as term",
            {},
        )
        return t_result

    # ####################################################################### #
    # ORIGINS
    # ####################################################################### #

    def get_list_of_origins(self, dummy=None):
        origins = self.mdb.get_origins()
        result = [{x["o"]["nanoid"]: x["o"]["name"]} for x in origins]
        if result:
            return result
        return []

    def get_origin_by_id(self, oid):
        result = self.mdb.get_origin_by_id(oid)
        return result

    # TAGS

    def get_tagged_entities(self, tag_key, tag_value=None):
        props = "{key:$key, value:$value}" if tag_value else "{key:$key}"
        ents_by_tag = self.get_with_statement(
            f"match (t:tag {props}) "
            "with t "
            "match (e)-[:has_tag]->(t) "
            "with t, {type:head(labels(e)), ent:e} as ee "
            "return t.key as tag_key, t.value as tag_value, collect(ee) as entities",
            {"key": tag_key, "value": tag_value},
        )

        for i in range(len(ents_by_tag)):
            for j in range(len(ents_by_tag[i]["entities"])):
                ents_by_tag[i]["entities"][j]["plural"] = plural[
                    ents_by_tag[i]["entities"][j]["type"]
                ]
        return ents_by_tag

    def get_tags_and_values(self):
        tags = self.mdb.get_tags_and_values()
        return tags

    # SEARCH

    def search_entity_handles(self, qstring):
        res = {}
        res["nodes"] = self.mdb.query_index("nodeHandle", qstring) or []
        res["properties"] = self.mdb.query_index("propHandle", qstring) or []
        res["relationships"] = self.mdb.query_index("edgeHandle", qstring) or []
        return res

    def search_terms(self, qstring, search_values=True, search_definitions=True):
        return self.mdb.search_terms(
            qstring,
            search_values=search_values,
            search_definitions=search_definitions,
        )

    # ####################################################################### #
    # CDE PVs & Synonyms
    # ####################################################################### #

    @functools.lru_cache
    @staticmethod
    def get_model_pvs_synonyms(model: str | None = None, version: str | None = None):
        qry = (
            "MATCH (n {model: $dataCommons, version: $version})-[:has_property]->"
            "(p:property) "
            "WITH collect(p) AS props "
            "UNWIND props AS prop "
            "OPTIONAL MATCH (prop)-[:has_concept]->(c:concept)<-[:represents]-"
            "(cde:term) WHERE toLower(cde.origin_name) CONTAINS 'cadsr' "
            "OPTIONAL MATCH (prop)-[:has_value_set]->(:value_set)-[:has_term]->(t:term)"
            " WITH prop, cde.origin_id AS CDECode, cde.origin_version AS CDEVersion, "
            "cde.value AS CDEFullName, cde.origin_id + '|' + "
            "COALESCE(cde.origin_version, '') AS cde_hdl, collect(t) AS model_pvs, "
            "CASE WHEN cde IS NOT NULL THEN true ELSE false END AS has_cde "
            "OPTIONAL MATCH (v:value_set {handle: cde_hdl})-[:has_term]->(cde_pv:term) "
            "WITH prop, CDECode, CDEVersion, CDEFullName, model_pvs, has_cde, "
            "collect(cde_pv) AS cde_pvs WITH prop, CDECode, CDEVersion, CDEFullName, "
            "model_pvs, has_cde, cde_pvs, CASE WHEN has_cde AND size(cde_pvs) > 0 "
            "AND NONE(p in cde_pvs WHERE p.value =~ 'https?://.*') THEN cde_pvs "
            "WHEN has_cde and size(cde_pvs) > 0 "
            "AND ANY(p in cde_pvs WHERE p.value =~ 'https?://.*') "
            "AND size(model_pvs) > 0 THEN model_pvs "
            "WHEN NOT has_cde AND size(model_pvs) > 0 THEN model_pvs "
            "ELSE [null] END AS pvs "
            "UNWIND pvs AS pv "
            "OPTIONAL MATCH (pv)-[:represents]->(c_cadsr:concept)<-[:represents]-"
            "(ncit_term:term {origin_name: 'NCIt'}), "
            "(c_cadsr)-[:has_tag]->(:tag {key: 'mapping_source', value: 'caDSR'}) "
            "OPTIONAL MATCH (ncit_term)-[:represents]->(c_ncim:concept)<-[:represents]"
            "-(syn:term), "
            "(c_ncim)-[:has_tag]->(:tag {key: 'mapping_source', value: 'NCIm'}) "
            "WHERE pv <> syn and pv.value <> syn.value "
            "WITH prop, CDECode, CDEVersion, CDEFullName, model_pvs, "
            "pv.value AS pv_val, ncit_term.origin_id AS ncit_oid, ncit_term.value "
            "AS ncit_value, collect(DISTINCT syn.value) AS distinct_syn_vals "
            "WITH prop, CDECode, CDEVersion, CDEFullName, model_pvs, pv_val, ncit_oid, "
            "CASE WHEN ncit_value IS NOT NULL THEN distinct_syn_vals + [ncit_value] "
            "ELSE distinct_syn_vals END AS syn_vals "
            "WITH prop, CDECode, CDEVersion, CDEFullName, model_pvs, "
            "collect({value: pv_val, synonyms: syn_vals, ncit_concept_code: ncit_oid}) AS formatted_pvs "  # noqa: E501
            "RETURN $dataCommons AS dataCommons, $version AS version, "
            "prop AS property, CDECode, CDEVersion, CDEFullName, "
            "formatted_pvs AS permissibleValues"
        )

        parms = {"dataCommons": model, "version": version}

        return mdb.mdb_.get_with_statement(qry, parms)

    @functools.lru_cache
    @staticmethod
    def get_cde_pvs_by_id(id: str | None = None, version: str | None = None):
        """Get CDE PVs and synonyms for a given CDE id and optional version."""
        qry = (
            "MATCH (cde:term {origin_id: $cde_id}) "
            "WHERE ($cde_version = '' OR cde.origin_version = $cde_version) "
            "OPTIONAL MATCH (vs:value_set)-[:has_term]->(pv:term) "
            "WHERE vs.handle = $cde_id + '|' + coalesce(cde.origin_version, '') "
            "WITH cde, vs.url as value_set_url, COLLECT(pv) as pvs "
            "WITH cde, value_set_url, pvs, "
            "CASE WHEN size(pvs) > 0 THEN pvs ELSE [null] END as pvs_to_process "
            "UNWIND pvs_to_process AS pv "
            "OPTIONAL MATCH (pv)-[:represents]->(c_cadsr:concept)<-[:represents]-"
            "(ncit_term:term {origin_name: 'NCIt'}), "
            "(c_cadsr)-[:has_tag]->(:tag {key: 'mapping_source', value: 'caDSR'}) "
            "WHERE pv IS NOT NULL "
            "OPTIONAL MATCH (ncit_term)-[:represents]->(c_ncim:concept)<-[:represents]"
            "-(syn:term), "
            "(c_ncim)-[:has_tag]->(:tag {key: 'mapping_source', value: 'NCIm'}) "
            "WHERE pv IS NOT NULL AND pv <> syn and pv.value <> syn.value "
            "WITH cde, value_set_url, pvs, "
            "CASE WHEN pv IS NULL THEN null ELSE pv.value END as pv_val, "
            "CASE WHEN pv IS NULL THEN null ELSE ncit_term.origin_id END AS ncit_oid, "
            "CASE WHEN pv IS NULL THEN null ELSE ncit_term.value END AS ncit_value, "
            "collect(DISTINCT syn.value) AS distinct_syn_vals "
            "WITH cde, value_set_url, pvs, "
            "CASE WHEN pv_val IS NULL THEN [] "
            "ELSE COLLECT({value: pv_val, synonyms: CASE WHEN ncit_value IS NOT NULL THEN "
            "distinct_syn_vals + [ncit_value] ELSE distinct_syn_vals END, "
            "ncit_concept_code: ncit_oid}) END AS permissibleValues "
            "RETURN cde, value_set_url, pvs, permissibleValues"
        )
        parms = {"cde_id": id, "cde_version": version}

        return mdb.mdb_.get_with_statement(qry, parms)

    @functools.lru_cache
    @staticmethod
    def get_term_nanoid_by_origin(
        origin_name: str | None = None,
        origin_id: str | None = None,
        origin_version: str | None = None,
    ):
        """Get terms by origin, origin_id, and origin_version."""
        qry = (
            "MATCH (t:term) WHERE t.origin_name = $origin_name "
            "AND t.origin_id = $origin_id AND ($origin_version IS NULL "
            "OR $origin_version = '' OR t.origin_version = $origin_version) "
            "WITH t ORDER by split(t.origin_version, '.') DESC "
            "RETURN t.nanoid as term_nanoid"
        )
        parms = {
            "origin_name": origin_name,
            "origin_id": origin_id,
            "origin_version": origin_version,
        }

        return mdb.mdb_.get_with_statement(qry, parms)

    @functools.lru_cache
    @staticmethod
    def get_cde_pvs_and_synonyms_by_id(
        id: str | None = None,
        version: str | None = None,
    ):
        """Get CDE PVs for a given CDE id and optional version."""
        qry = (
            "MATCH (cde:term {origin_id: $cde_id}) "
            "WHERE ($cde_version = '' OR cde.origin_version = $cde_version) "
            "OPTIONAL MATCH (vs:value_set)-[:has_term]->(pv:term) "
            "WHERE vs.handle = $cde_id + '|' + coalesce(cde.origin_version, '') "
            "WITH cde, vs.url as value_set_url, COLLECT(pv) as pvs "
            "RETURN cde, vs.url as value_set_url, COLLECT(pv) as pvs"
        )
        parms = {"cde_id": id, "cde_version": version}

        return mdb.mdb_.get_with_statement(qry, parms)

    @functools.lru_cache
    @staticmethod
    def get_all_pvs_and_synonyms():
        """Get all CDE PVs and synonyms used by models in MDB."""
        qry = (
            "MATCH (cde:term) WHERE toLower(cde.origin_name) CONTAINS 'cadsr' WITH cde "
            "MATCH (ent)-[:has_property]->(p:property)-[:has_concept]->"
            "(:concept)<-[:represents]-(cde) WHERE p.model IS NOT NULL AND p.version "
            "IS NOT NULL WITH cde,COLLECT(DISTINCT {model: p.model, version: p.version,"
            " property: ent.handle + '.' + p.handle}) AS models "
            "WITH cde, models, cde.origin_id + '|' + COALESCE(cde.origin_version, '') "
            "AS cde_hdl "
            "OPTIONAL MATCH (prop: property)-[:has_concept]->(c:concept)<-[:represents]"
            "-(cde) OPTIONAL MATCH (prop)-[:has_value_set]->(:value_set)-[:has_term]->"
            "(model_pv:term) WITH cde, models, cde_hdl, COLLECT(DISTINCT model_pv) AS "
            "model_pvs OPTIONAL MATCH (vs:value_set {handle: cde_hdl})-[:has_term]->"
            "(cde_pv:term) WITH cde, models, model_pvs, COLLECT(DISTINCT cde_pv) AS "
            "cde_pvs WITH cde, models, model_pvs, cde_pvs, CASE WHEN size(cde_pvs) > 0 "
            "AND NONE(p in cde_pvs WHERE p.value =~ 'https?://.*') THEN cde_pvs "
            "WHEN size(cde_pvs) > 0 AND ANY(p in cde_pvs WHERE p.value =~ "
            "'https?://.*') AND size(model_pvs) > 0 THEN model_pvs "
            "ELSE [null] END AS pvs "
            "WHERE size(pvs) > 0 UNWIND pvs AS pv "
            "OPTIONAL MATCH (pv)-[:represents]->(c_cadsr:concept)<-[:represents]-"
            "(ncit_term:term {origin_name: 'NCIt'}), "
            "(c_cadsr)-[:has_tag]->(:tag {key: 'mapping_source', value: 'caDSR'}) "
            "OPTIONAL MATCH (ncit_term)-[:represents]->(c_ncim:concept)<-[:represents]"
            "-(syn:term), "
            "(c_ncim)-[:has_tag]->(:tag {key: 'mapping_source', value: 'NCIm'}) "
            "WHERE pv IS NOT NULL AND pv <> syn and pv.value <> syn.value "
            "WITH cde, pv, models, pv.value as pv_val, ncit_term.origin_id AS ncit_oid,"
            " ncit_term.value AS ncit_value, COLLECT(DISTINCT syn.value) "
            "AS distinct_syn_vals WITH cde, models, pv_val, ncit_oid, "
            "CASE WHEN ncit_value IS NOT NULL THEN distinct_syn_vals + [ncit_value] "
            "ELSE distinct_syn_vals END AS syn_vals "
            "WITH cde, models, CASE WHEN pv_val IS NOT NULL THEN "
            "COLLECT({value: pv_val, synonyms: syn_vals, ncit_concept_code: ncit_oid}) "
            "ELSE [] END AS formatted_pvs "
            "RETURN cde.origin_id AS CDECode, cde.origin_version AS CDEVersion, "
            "cde.value AS CDEFullName, models, formatted_pvs AS permissibleValues "
        )
        return mdb.mdb_.get_with_statement(qry, {})
