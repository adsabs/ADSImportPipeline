
# on localhost:
#  uses libxml2 via virtualenv --system-site-packages
#  and adspy via mount of /proj

import sys
from datetime import datetime
try:
    import ads.ADSCachedExports as ads_ex
    import ads.journal_parser as ads_jp
    import ads.Keywords as kw_normalizer
    import ads.ArtDefs as ArtDefs
except ImportError:
    sys.path.append('/proj/ads/soft/python/lib/site-packages')
    try:
        import ads.ADSCachedExports as ads_ex
        import ads.journal_parser as ads_jp
        import ads.Keywords as kw_normalizer
        import ads.ArtDefs as ArtDefs
    except ImportError as e:
        print 'Unable to import ads libraries: {}'.format(e)


def add_direct(record, json_timestamp=None, created_date=None,
               origin=None, matched_preprint=False, fulltext=None):
    """
    return a complete ADSRecords instance from direct data with xml
    """
    bibcode = record['bibcode']
    if not bibcode:
        raise ads_ex.InvalidBibcode('Empty bibcode.')

    adsr = ads_ex.ADSRecords('full', 'XML', cacheLooker=False)
    # bibliographic_info = ads_ex.get_bibliographic_info(bibcode)

    # create a new record for the Direct entry

    if created_date is None:
        # created_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S%fZ')
        created_date = ads_ex.iso_8601_time(None)

    print "HI CREATED DATE IS:",created_date
    rec_properties = {'bibcode': bibcode, 'entry_date': created_date}
    adsr.current_record = ads_ex.xml_node(adsr.xml_records, 'record', properties=rec_properties)

    # create a new metadata tag for the Direct entry abstract
    datasource = 'ARXIV'
    abs_properties = {'origin': datasource, 'type': 'general', 'primary': 'True', 'alternate_journal': 'False'}
    adsr.current_abstract = ads_ex.xml_node(adsr.current_record, 'metadata', properties=abs_properties)

    # begin creating subfields under this metadata tag

#   creation_time = ads_ex.iso_8601_time(None)
#   modif_time = creation_time
    creation_time = created_date
    modif_time = ads_ex.iso_8601_time(None)
    ads_ex.xml_node(adsr.current_abstract, 'creation_time', creation_time)
    ads_ex.xml_node(adsr.current_abstract, 'modification_time', modif_time)

    ads_ex.xml_node(adsr.current_abstract, 'bibcode', bibcode)

    (year, month, dum) = record['pubdate'].split('-')
    dates = {'date-preprint': '%s-%s-00' % (year, month)}
    ads_ex.add_dates(adsr.current_abstract, dates)

    title = record['title'].replace('\n ','')
    ads_ex.xml_node(adsr.current_abstract, 'title', title)

    abstract_field = record['abstract']
    abstract_field = ads_ex.UNICODE_HANDLER.remove_control_chars(abstract_field)
    try:
        abstract_field = ads_ex.UNICODE_HANDLER.ent2xml(abstract_field)
    except:
        pass
    ads_ex.xml_node(adsr.current_abstract, 'abstract', abstract_field.strip())

    authors = ads_ex.UNICODE_HANDLER.ent2u(record['authors'])
    authors = ads_ex.UNICODE_HANDLER.remove_control_chars(authors)
    authors = ads_ex.RE_INITIAL.sub('. ', authors)
    authors = authors.strip().strip(';')
    author_number = 0
    for index, author_name in enumerate(authors.split(';')):
        normalized_author = ads_ex.normalize_author(author_name)
        author_number += 1
        author = {
            'nr': str(author_number),
            'western': author_name.strip(),
            'normalized': normalized_author,
            'affiliation': None,
            'id': None,
            'email': None,
            'native': None,
            'author_id': None,
            'type': 'regular'
            }
        ads_ex.add_author(adsr.current_abstract, author, 'full')

    journal = record['publication']
    ads_ex.xml_node(adsr.current_abstract, 'journal', journal)

    canonical_journal = ads_jp.get_canonical_journal(bibcode)
    ads_ex.xml_node(adsr.current_abstract, 'canonical_journal', canonical_journal)

    electronic_id = journal.replace('eprint ', '')
    ads_ex.xml_node(adsr.current_abstract, 'electronic_id', electronic_id)

    number_pages = 0
    ads_ex.xml_node(adsr.current_abstract, 'number_pages', str(number_pages))

    databases = set()
    try:
        field = ads_ex.UNICODE_HANDLER.ent2xml(record['keywords'])
    except:
        try:
            field = record['keywords']
        except:
            pass
    if len(field) > 0:
        adsr.arxiv_categories = ads_ex.xml_node(adsr.current_abstract, 'arxivcategories')
        all_keywords = {}
        keywords = []
        main_category = 'main'
        for keyword in field.split(';'):
            keyword = keyword.strip()
            try:
                category = ArtDefs.cat2channel[keyword]
            except:
                pass
            else:
                ads_ex.xml_node(adsr.arxiv_categories, 'arxivcategory', category, {'type': main_category})
                if category.find('.') >= 0:
                    category = category.split('.')[0]
                try:
                    databases.add(ads_ex.ARXIV_DATABASE[category])
                except:
                    pass
                main_category = None
                keywords.append((keyword, kw_normalizer.get_normalized_keyword(keyword)))
    all_keywords.setdefault('arXiv', []).extend(keywords)
    ads_ex.add_keywords(adsr.current_abstract, all_keywords)

    pubnote = "; ".join([x.replace('\n', '') for x in record['comments']])
    ads_ex.xml_node(adsr.current_abstract,'pubnote', pubnote.replace('  ', ' '))

    # Properties
    adsr.current_properties = ads_ex.xml_node(adsr.current_record, 'metadata',
                                              properties={'type': 'properties',
                                                          'primary': 'False',
                                                          'origin': 'ADS metadata',
                                                          'alternate_journal': 'False'})

    ads_ex.xml_node(adsr.current_properties, 'JSON_timestamp', ' dummy string')
    ads_ex.add_databases(adsr.current_properties, databases)
    ads_ex.xml_node(adsr.current_properties, 'pubtype', 'eprint')
    ads_ex.xml_node(adsr.current_properties, 'private', 0)
    ads_ex.xml_node(adsr.current_properties, 'ocrabstract', 0)
#   preprint_id = electronic_id.replace('arXiv:', '')
    preprint_id = electronic_id
    ads_ex.xml_node(adsr.current_properties, 'preprint', preprint_id)
    ads_ex.xml_node(adsr.current_properties, 'nonarticle', 0)
    ads_ex.xml_node(adsr.current_properties, 'refereed', 0)
    ads_ex.xml_node(adsr.current_properties, 'openaccess', 1)
    ads_ex.xml_node(adsr.current_properties, 'eprint_openaccess', 1)
    ads_ex.xml_node(adsr.current_properties, 'pub_openaccess', 0)
    ads_ex.xml_node(adsr.current_properties, 'note', 0)
    ads_ex.xml_node(adsr.current_properties, 'ads_openaccess', 0)

    # Relations
    adsr.current_relations = ads_ex.xml_node(adsr.current_record, 'metadata',
                                             properties={'type': 'relations',
                                                         'primary': 'False',
                                                         'origin': 'ADS metadata',
                                                         'alternate_journal': 'False'})

    ads_ex.xml_node(adsr.current_relations, 'preprintid', preprint_id, {'ecode': bibcode})
    ads_ex.xml_node(adsr.current_relations, 'alternates', None)

    adsr.linksection = ads_ex.xml_node(adsr.current_relations, 'links')
    ads_ex.xml_node(adsr.linksection, 'link',
                    properties={'type': 'preprint',
                                'url': record['properties']['HTML'],
                                'access': 'open'})

    return adsr


