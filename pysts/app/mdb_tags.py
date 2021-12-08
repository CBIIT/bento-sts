from flask import current_app
from collections import namedtuple


class mdb_tags:
    """Mixin for reading MDB Tags and customizing UI functionality 
based on them."""

    # ###################################################################### #
    # DATA SUBSETS / TAGS
    # ###################################################################### #

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
            # formatted_tags = self.format_tags_records(tag_records)
        # return formatted_tags

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
