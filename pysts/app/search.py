from flask import current_app
import pprint

def add_to_index(index, entity):
    """ updating to use mdb fields """

    index="default"
    
    #if not current_app.elasticsearch:
    #    return

    # cleanup primary string handle - make easy for match
    # turn 'study_site' to 'study site' for ease of matching
    primary_cleaned = ''
    primary = ''
    if 'handle' in entity:
        primary_cleaned = entity['handle']
        primary = entity['handle']
    else:
        primary_cleaned = entity['value']
        primary = entity['value']
    primary_cleaned = primary_cleaned.replace("_", '')
    primary_cleaned = primary_cleaned.replace("-", '')

    payload = {
        'id': entity['id'],
        'primary_': primary_cleaned,
        'primary': primary,
        'type': entity['type'],
        'link': entity['link']
    }

    current_app.elasticsearch.index(index=index, id=entity['link'], body=payload)


def remove_from_index(index, model):
    """ REFACTOR: refactor to mdb """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def totally_scrub_index(index):
    """ REFACTOR: refactor to mdb """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index='default', id='all')


def query_index(index, query, page, per_page):
    """ REFACTOR: model to mdb """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index="default",
        body={
            "query": {"multi_match": {"query": query, "fields": ["primary", "primary_", "handle", "value", "desc"]}},
            "from": (page - 1) * per_page,
            "size": per_page,
        },
    )

    if(0):
        pprint.pprint('search results are ...')
        pprint.pprint(search)
    
        ids = [hit["_id"] for hit in search["hits"]["hits"]]
        pprint.pprint('ids i got back are...')
        pprint.pprint(ids)

        names = [hit["_source"]["primary"] for hit in search["hits"]["hits"]]
        pprint.pprint('names i got back are...')
        pprint.pprint(names)

        links = [hit["_source"]["link"] for hit in search["hits"]["hits"]]
        pprint.pprint('links i got back are...')
        pprint.pprint(links)

        types = [hit["_source"]["type"] for hit in search["hits"]["hits"]]
        pprint.pprint('types i got back are...')
        pprint.pprint(types)
        print("------")
        print("------")

    names = [hit["_source"]["primary"] for hit in search["hits"]["hits"]]
    links = [hit["_source"]["link"] for hit in search["hits"]["hits"]]
    types = [hit["_source"]["type"] for hit in search["hits"]["hits"]]

    # zip arrays into dict, for ease of result presentation
    #result = dict(zip(names, links, types))
    #print("returning")
    #pprint.pprint(result)

    results=[]
    for idx,val in enumerate(names):
        hit = { 'name': names[idx],
                'link': links[idx],
                'type': types[idx] }
        results.append(hit)

    return results, search["hits"]["total"]["value"]
