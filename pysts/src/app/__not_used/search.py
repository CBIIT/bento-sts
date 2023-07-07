from flask import current_app


def add_to_index(entity):
    """ REFACTOR: updating to use mdb fields """
    index = "mdb"

    # this disables elasticsearch if it isn't configured/
    # aka  env ELASTICSEARCH_URL is not set
    if not current_app.elasticsearch:
        return

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

    current_app.elasticsearch.index(index=index, id=entity['id'], body=payload)


def remove_from_index(entity):
    """ REFACTOR: refactor to mdb """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index="mdb", id=entity['id'])


def query_index(index, query, page, per_page):
    """ REFACTOR: model to mdb """
    if not current_app.elasticsearch:
        return [], 0

    search = current_app.elasticsearch.search(
        index="mdb",
        body={
            "query": {"multi_match": {"query": query, "fields": ["*"]}},
            "from": (page - 1) * per_page,
            "size": per_page,
        },
    )

    ids   = [hit["_id"] for hit in search["hits"]["hits"]]
    names = [hit["_source"]["primary"] for hit in search["hits"]["hits"]]
    links = [hit["_source"]["link"] for hit in search["hits"]["hits"]]
    types = [hit["_source"]["type"] for hit in search["hits"]["hits"]]

    # 3-way zip arrays into dict, for ease of showing on search results page
    results = []
    for idx, val in enumerate(ids):
        hit = {'name': names[idx],
               'link': links[idx],
               'type': types[idx]}
        results.append(hit)

    return results, search["hits"]["total"]["value"]
