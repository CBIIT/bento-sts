package Bento::STS::CypherQueries;
use base Exporter;
#use strict;
our @EXPORT;

@EXPORT = qw/%queries/;

our %queries = (

    #// query 3 get properties
    get_properties => <<Q,
        MATCH (p:property {value_domain:"enum"}) -[:has_value_set]-> (v:value_set) 
        RETURN DISTINCT p.handle, p.value_domain, p.model, v.id, v.url
Q

    #// get the version of the database, used in healthcheck that we can query the database
    #// but does not require that the database have any data
    get_database_version => <<Q,
       	call dbms.components() 
	    yield name, versions, edition unwind versions as version 
        return name, version, edition;
Q

    get_database_node_count => <<Q,
        MATCH (n)
        RETURN count(n) as count
Q

    ## -----------------------------------##

    ## 
    get_list_of_models => <<Q,
        MATCH (n:node)
        RETURN DISTINCT n.model
Q

    ##
	get_model_by_name => <<'Q',
        MATCH (n:node)
        WHERE n.model = $param 
		RETURN DISTINCT n.model
Q

    ## 
    get_list_of_nodes => <<Q,
	    MATCH (n:node)
    	RETURN DISTINCT n.nanoid6, n.handle, n.model
Q


    ## 
	#// idea: n3 -> n1 --> n2
    get_node_by_id => <<'Q',
	    MATCH (n1:node)				
		WHERE n1.nanoid6 = $param
    	OPTIONAL MATCH (n1)<-[:has_src]-(r12:relationship)-[:has_dst]->(n2:node)
	    OPTIONAL MATCH (n3)<-[:has_src]-(r31:relationship)-[:has_dst]->(n1:node)
    	OPTIONAL MATCH (n1)-[:has_property]->(p1:property)
    	OPTIONAL MATCH (n1)-[:has_concept]->(c1:concept)
    	OPTIONAL MATCH (ct:term)-[:represents]->(c1)
    	OPTIONAL MATCH (ct)-[:has_origin]->(o:origin)
    	RETURN DISTINCT n1.nanoid6 as `node-id`,
						n1.handle as `node-handle`, 
            			n1.model as `node-model`, 
            			r12.handle as `to-relationship`,
						n2.nanoid6 as `to-node`, 
            			n2.handle, 
						n2.model,
            			r31.handle,
						n3.nanoid6, 
            			n3.handle,
						n3.model, 
            			p1.nanoid6,
						p1.handle,
						p1.value_domain,
						p1.model
						//c1.id, 
            			//ct.nanoid6,
						//ct.value, 
            			//ct.origin_id, 
            			//ct.origin_definition, 
						//ct.comments, 
            			//ct.notes,
            			//o.name
                        ;
Q
   


    #// property - detail
    get_property_by_id => <<'Q',
	MATCH (p:property)
    WHERE p.nanoid6 = $param
	OPTIONAL MATCH (p)-[:has_value_set]->(vs)
    OPTIONAL MATCH (vs)-[:has_term]->(t:term)
	RETURN DISTINCT 
            p.nanoid6,
            p.handle as `property-handle`, 
			p.model as `property-model`, 
			p.value_domain as `property-value_domain`, 
			p.is_required ,  
			vs.nanoid6,
			vs.url as `property-value_set-url`,
            COUNT(DISTINCT(t.nanoid6));
Q


    #// value_set - list
    get_list_of_valuesets => <<'Q',
    	MATCH (vs:value_set)
    	MATCH (p:property)-[:has_value_set]->(vs)
    	OPTIONAL MATCH (p)-[:has_concept]->(cp:concept)
    	OPTIONAL MATCH (ct:term)-[:represents]->(cp)
    	OPTIONAL MATCH (vs)-[:has_term]->(t:term)
    	OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
    	OPTIONAL MATCH (vs)-[:has_origin]->(vso:origin)
    	RETURN DISTINCT 
            p.nanoid6,
            p.handle as `property-handle`, 
			p.model as `property-model`,
			vs.nanoid6 as `value_set-id`, 
			vs.url as `value_set-url`, 
			t.nanoid6 as `term-id`, 
			t.value as `term-value` ;
Q


    #// value_set - detail
    get_valueset_by_id => <<'Q',
    	MATCH (vs:value_set)
        WHERE vs.nanoid6 = $param
    	OPTIONAL MATCH (p:property)-[:has_value_set]->(vs)
    	OPTIONAL MATCH (p)-[:has_concept]->(cp:concept)
    	OPTIONAL MATCH (ct:term)-[:represents]->(cp)
    	OPTIONAL MATCH (vs)-[:has_term]->(t:term)
    	OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
    	OPTIONAL MATCH (vs)-[:has_origin]->(vso:origin)
    	RETURN DISTINCT 
            p.nanoid6, 
            p.handle as `property-handle`, 
			p.model as `property-model`,
			vs.nanoid6 as `value_set-id`, 
			vs.url as `value_set-url`, 
			t.nanoid6 as `term-id`, 
			t.value as `term-value`;
Q


    #// term - list
    get_list_of_terms => <<Q,
        MATCH (vs:value_set) -[:has_term]->(t:term)
        OPTIONAL MATCH (t)-[:has_origin]->(to:origin)
        RETURN DISTINCT  
                        t.value as `term-value`, 
                        t.nanoid6 as `term-id`,  
                        to.name as `origin`;
Q


    #// term - detail
    get_term_by_id => <<'Q',
        MATCH (vs:value_set)-[:has_term]->(t:term)
        WHERE t.nanoid6 = $param 
        OPTIONAL MATCH (t)-[:represents]->(cp:concept)
        OPTIONAL MATCH (t)-[:has_origin]->(to:origin)
        RETURN DISTINCT t.value as `term-value`, 
                        t.nanoid6 as `term-id`, 
                        to.name as `origin-name`,
                        cp.nanoid6 as `concept-id`,
                        vs.url as `value_set-url`, 
                        vs.id as `value_set-id`;
Q


    #// term - detail
    get_term_by_name => <<'Q',
        MATCH (vs:value_set)-[:has_term]->(t:term)
        WHERE t.value = $param 
        OPTIONAL MATCH (t)-[:represents]->(cp:concept)
        OPTIONAL MATCH (t)-[:has_origin]->(to:origin)
        RETURN DISTINCT t.value as `term-value`, 
                        t.nanoid6 as `term-id`, 
                        to.name as `origin-name`,
                        cp.nanoid6 as `concept-id`,
                        vs.url as `value_set-url`, 
                        vs.nanoid6 as `value_set-id`;
Q

    #// refactored above 

    get_all_node_details => <<'Q',
	    MATCH (n1:node)				
    	OPTIONAL MATCH (n1)<-[:has_src]-(r12:relationship)-[:has_dst]->(n2:node)
	    OPTIONAL MATCH (n3)<-[:has_src]-(r31:relationship)-[:has_dst]->(n1:node)
    	OPTIONAL MATCH (n1)-[:has_property]->(p1:property)
    	OPTIONAL MATCH (n1)-[:has_concept]->(c1:concept)
    	OPTIONAL MATCH (ct:term)-[:represents]->(c1)
    	OPTIONAL MATCH (ct)-[:has_origin]->(o:origin)
    	RETURN DISTINCT n1.id as `node-id`,
						n1.handle as `node-handle`, 
            			n1.model as `node-model`, 
            			r12.handle as `to-relationship`,
						n2.id as `to-node`, 
            			n2.handle, 
						n2.model,
            			r31.handle,
						n3.id, 
            			n3.handle,
						n3.model, 
            			p1.id,
						p1.handle,
						p1.value_domain,
						p1.model,
						c1.id, 
            			ct.id,
						ct.value, 
            			ct.origin_id, 
            			ct.origin_definition, 
						ct.comments, 
            			ct.notes,
            			o.name;
Q

    #// node - detail
	#// idea: n3 -> n1 --> n2
    get_node_details => <<'Q',
	    MATCH (n1:node)				
		WHERE n1.id = $param
    	OPTIONAL MATCH (n1)<-[:has_src]-(r12:relationship)-[:has_dst]->(n2:node)
	    OPTIONAL MATCH (n3)<-[:has_src]-(r31:relationship)-[:has_dst]->(n1:node)
    	OPTIONAL MATCH (n1)-[:has_property]->(p1:property)
    	OPTIONAL MATCH (n1)-[:has_concept]->(c1:concept)
    	OPTIONAL MATCH (ct:term)-[:represents]->(c1)
    	OPTIONAL MATCH (ct)-[:has_origin]->(o:origin)
    	RETURN DISTINCT n1.id as `node-id`,
						n1.handle as `node-handle`, 
            			n1.model as `node-model`, 
            			r12.handle as `to-relationship`,
						n2.id as `to-node`, 
            			n2.handle, 
						n2.model,
            			r31.handle,
						n3.id, 
            			n3.handle,
						n3.model, 
            			p1.id,
						p1.handle,
						p1.value_domain,
						p1.model,
						c1.id, 
            			ct.id,
						ct.value, 
            			ct.origin_id, 
            			ct.origin_definition, 
						ct.comments, 
            			ct.notes,
            			o.name;
Q

get_model_nodes => <<'Q',
	    MATCH (n1:node)				
		WHERE n1.model = $param
    	OPTIONAL MATCH (n1)<-[:has_src]-(r12:relationship)-[:has_dst]->(n2:node)
	    OPTIONAL MATCH (n3)<-[:has_src]-(r31:relationship)-[:has_dst]->(n1:node)
    	OPTIONAL MATCH (n1)-[:has_property]->(p1:property)
    	OPTIONAL MATCH (n1)-[:has_concept]->(c1:concept)
    	OPTIONAL MATCH (ct:term)-[:represents]->(c1)
    	OPTIONAL MATCH (ct)-[:has_origin]->(o:origin)
    	RETURN DISTINCT n1.id as `node-id`,
						n1.handle as `node-handle`;
Q

    #// property - list
    get_properties_list => <<Q,
	    MATCH (p:property) 
    	RETURN DISTINCT p.handle as `property-handle`, p.value_domain, p.model, p.is_required ;
Q



    #// value_set - list
    get_value_set_list => <<'Q',
    	MATCH (vs:value_set)
    	MATCH (p:property)-[:has_value_set]->(vs)
    	OPTIONAL MATCH (p)-[:has_concept]->(cp:concept)
    	OPTIONAL MATCH (ct:term)-[:represents]->(cp)
    	OPTIONAL MATCH (vs)-[:has_term]->(t:term)
    	OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
    	OPTIONAL MATCH (vs)-[:has_origin]->(vso:origin)
    	RETURN DISTINCT p.handle as `property-handle`, 
			p.model as `property-model`,
			vs.id as `value_set-id`, 
			vs.url as `value_set-url`, 
			t.id as `term-id`, 
			t.value as `term-value`;
Q


    #// value_set - detail
    get_model_value_sets => <<'Q',
    	MATCH (p:property)-[:has_value_set]->(vs:value_set)
    	WHERE p.model = $param
		MATCH (vs)-[:has_handle]->(vsh:value_set_handle)
    	OPTIONAL MATCH (vs)-[:has_term]->(t:term)
		OPTIONAL MATCH (t)-[:has_handle]->(th:term_handle)
    	OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
    	RETURN DISTINCT 
			vs.id as `value_set-id`, 
			vsh.id as `value_set_handle-id`,
			vsh.handle as `value_set_handle-handle`, 
			vsh.url as `value_set-url`, 
			t.id as `term-id`, 
			th.value as `term-handle`;
Q


    #// concept - list
    concepts_list => <<Q,
	    MATCH (c:concept)
	    MATCH (ct:term)-[:represents]->(c)
	    RETURN DISTINCT c.id as `concept-id`, 
			ct.value as `concept-term-value`; 
Q

    #// concept - detail
    concepts_detail => <<Q,
    	MATCH (c:concept)
    	MATCH (ct:term)-[:represents]->(c)
    	OPTIONAL MATCH (ct)-[:has_origin]->(cto:origin)
    	OPTIONAL MATCH (n:node)-[:has_concept]->(c)
    	OPTIONAL MATCH (p:property)-[:has_concept]->(c)
    	OPTIONAL MATCH (r:relationship)-[:has_concept]->(c)
	    RETURN DISTINCT c.id as `concept-id`, 
			ct.value as `concept-term-value`, 
			ct.id as `concept-term-id`, 
			ct.origin_id as `concept-term-origin_id`, 
			ct.origin_definition as `concept-term-origin-definition`, 
			cto.name as `concept-term-origin-name`, 
			n.handle, 
			p.handle, 
			r.handle;
Q

);

1;
