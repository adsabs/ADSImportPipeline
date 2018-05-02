def translate(record, **kwargs):

# takes an input json object from an adsabs-pyingest parser
# and re-serializes it into a form used by denormalized
# records.

    try:
        record['title']
    except:
        pass
    else:
        record['title'] = [record['title']]

    try:
        record['authors']
    except:
        pass
    else:
        record['author'] = [record['authors']]
        del record['authors']

    try:
        record['affiliations']
    except:
        pass
    else:
        record['aff'] = record['affiliations']
        del record['affiliations']

    try:
        record['keywords']
    except:
        pass
    else:
        record['keyword'] = [record['keywords']]
        del record['keywords']

    try:
        record['properties']
    except:
        pass
    else:
        del record['properties']

    try:
        record['publication']
    except:
        pass
    else:
        record['pub'] = record['publication']
        del record['publication']

    try:
        record['page']
    except:
        pass
    else:
        record['page'] = [record['page']]

    return record
