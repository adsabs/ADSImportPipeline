import ads.ADSCachedExports as ads_ex
import ads.journal_parser as ads_jp
import ads.Keywords as kw_normalizer
import ads.ArtDefs as ArtDefs
import pyingest.parsers.arxiv as arxiv
import pyingest.serializers.classic as classic

class adsDirectRecord(ads_ex.ADSRecords):

    def addDirect(self, record, json_timestamp=None,current_record=None,
            origin=None, matched_preprint=False, fulltext=None):

        bibcode = record['bibcode']
        if not bibcode:
            raise ads_ex.InvalidBibcode('Empty bibcode.')

        bibliographic_info = ads_ex.get_bibliographic_info(bibcode)

# create a new record for the Direct entry

        if current_record is None:
            rec_properties = {'bibcode': bibcode,'entry_date': record['pubdate']}
            self.current_record = ads_ex.xml_node(self.xml_records, 'record', properties=rec_properties)
        else:
            self.current_record = current_record

# create a new metadata tag for the Direct entry abstract
        datasource = 'ARXIV'
        abs_properties = {'origin':datasource, 'type':'general', 'primary':'True', 'alternate_journal':'False'}
        self.current_abstract = ads_ex.xml_node(self.current_record, 'metadata', properties = abs_properties)


# begin creating subfields under this metadata tag

        creation_time = ads_ex.iso_8601_time(None)
        modif_time = creation_time
        ads_ex.xml_node(self.current_abstract, 'creation_time', creation_time)
        ads_ex.xml_node(self.current_abstract, 'modification_time', modif_time)

        ads_ex.xml_node(self.current_abstract, 'bibcode', bibcode)

        (year,month,dum) = record['pubdate'].split('-')
        dates = {'date-preprint':'%s-%s-00'%(year,month)}
        ads_ex.add_dates(self.current_abstract, dates)

        ads_ex.xml_node(self.current_abstract, 'title', record['title'])

        abstract_field = record['abstract']
        abstract_field = ads_ex.UNICODE_HANDLER.remove_control_chars(abstract_field)
        try:
            abstract_field = ads_ex.UNICODE_HANDLER.ent2xml(abstract_field)
        except:
            pass
        ads_ex.xml_node(self.current_abstract, 'abstract', abstract_field.strip())

        authors = ads_ex.UNICODE_HANDLER.ent2u(record['authors'])
        authors = ads_ex.UNICODE_HANDLER.remove_control_chars(authors)
        authors = ads_ex.RE_INITIAL.sub('. ', authors)
        authors = authors.strip().strip(';')
        xml_authors = []
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
            ads_ex.add_author(self.current_abstract,author,'full')


        
        journal = record['publication']
        ads_ex.xml_node(self.current_abstract,'journal',journal)

        canonical_journal = ads_jp.get_canonical_journal(bibcode)
        ads_ex.xml_node(self.current_abstract,'canonical_journal',canonical_journal)

        electronic_id = journal.replace('eprint ','')
        ads_ex.xml_node(self.current_abstract,'electronic_id',electronic_id)

        number_pages = 0
        ads_ex.xml_node(self.current_abstract,'number_pages',str(number_pages))

        databases = set()
        try:
            field = ads_ex.UNICODE_HANDLER.ent2xml(record['keywords'])
        except:
            pass
        else:
            self.arxiv_categories = ads_ex.xml_node(self.current_abstract,'arxivcategories')
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
                    ads_ex.xml_node(self.arxiv_categories,'arxivcategory',category,{'type': main_category})
                    if category.find('.') >= 0:
                        category = category.split('.')[0]
                    try:
                        databases.add(ads_ex.ARXIV_DATABASE[category])
                    except:
                        pass
                    main_category = None
                    keywords.append((keyword, kw_normalizer.get_normalized_keyword(keyword)))
            all_keywords.setdefault('arXiv',[]).extend(keywords)
            ads_ex.add_keywords(self.current_abstract, all_keywords)


        pubnote = ". ".join([x.replace('\n','') for x in record['comments']])
        ads_ex.xml_node(self.current_abstract,'pubnote',pubnote.replace('  ',' '))
        


        # Properties
        self.current_properties = ads_ex.xml_node(self.current_record, 'metadata',
                                         properties={'type': 'properties',
                                                     'primary':'False',
                                                     'origin': 'ADS metadata',
                                                     'alternate_journal':'False'})

        ads_ex.xml_node(self.current_properties,'JSON_timestamp','dummy string')
        ads_ex.add_databases(self.current_properties,databases)
        ads_ex.xml_node(self.current_properties,'pubtype','eprint')
        ads_ex.xml_node(self.current_properties,'private',0)
        ads_ex.xml_node(self.current_properties,'ocrabstract',0)
        preprint_id = electronic_id.replace('arXiv:','')
        ads_ex.xml_node(self.current_properties,'preprint',preprint_id)
        ads_ex.xml_node(self.current_properties,'nonarticle',0)
        ads_ex.xml_node(self.current_properties,'refereed',0)
        ads_ex.xml_node(self.current_properties,'openaccess',1)
        ads_ex.xml_node(self.current_properties,'eprint_openaccess',1)
        ads_ex.xml_node(self.current_properties,'pub_openaccess',0)
        ads_ex.xml_node(self.current_properties,'note',0)
        ads_ex.xml_node(self.current_properties,'ads_openaccess',0)


        # Relations
        self.current_relations = ads_ex.xml_node(self.current_record, 'metadata',
                                       properties={'type': 'relations',
                                                   'primary':'False',
                                                   'origin': 'ADS metadata',
                                                   'alternate_journal':'False'})

        ads_ex.xml_node(self.current_relations,'preprintid',preprint_id,{'ecode':bibcode})
        ads_ex.xml_node(self.current_relations,'alternates',None)

        self.linksection = ads_ex.xml_node(self.current_relations,'links')
        ads_ex.xml_node(self.linksection,'link',
                        properties={'type':'preprint',
                                    'url':record['properties']['HTML'],
                                    'access':'open'})

        # Done



def main():

    import gzip

    reclist = list()
#   meta_dir = '/proj/ads/abstracts/sources/ArXiv/oai/arXiv.org/'
#   reclist.append(meta_dir + '1711/05739')
#   reclist.append(meta_dir + '1710/08505')

    caldate = '2018-08-16'

    ARXIV_INCOMING_ABS_DIR = '/proj/ads/abstracts/sources/ArXiv'
    ARXIV_UPDATE_AGENT_DIR = ARXIV_INCOMING_ABS_DIR + '/UpdateAgent'
    ARXIV_ARCHIVE_ABS_DIR = ARXIV_INCOMING_ABS_DIR + '/oai/arXiv.org'

    logfile = ARXIV_UPDATE_AGENT_DIR + '/UpdateAgent.out.' + caldate + '.gz'
    with gzip.open(logfile,'r') as flist:
        for l in flist.readlines():
            # sample line: oai/arXiv.org/0706/2491 2018-06-13T01:00:29
            a = ARXIV_INCOMING_ABS_DIR + '/' + l.split()[0]
            reclist.append(a)

    for f in reclist:
        with open(f,'rU') as fp:
            input_doc = arxiv.ArxivParser()
            r = input_doc.parse(fp)
            output = adsDirectRecord('full','XML',cacheLooker=False)
            output.addDirect(r)
#           print output.root.serialize()
            output.write()

if __name__ == '__main__':
    main()
