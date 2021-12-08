import pprint
from flask import url_for, current_app
from bento_meta.mdb import MDB

class mdb_update():
    """Mixin for MDB containing database-write methods."""

    # NODES #
    
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

    # TERMS #
    
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

    # PROPERTIES #

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

    # TAGS #

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
