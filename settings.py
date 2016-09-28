import os
import sys

PROJECT_HOME = os.path.abspath(os.path.dirname(__file__))

SOLR_URLS=[
  'http://ads1/solr/update',
  'http://ads2/solr/update',
]

MONGO = {
  'HOST': os.environ.get('MONGO_HOST','localhost'),
  'PORT': os.environ.get('MONGO_PORT',27018),
  'DATABASE': os.environ.get('MONGO_DATABASE','ads'),
  'USER': None,    #May be set to None
  'PASSWD': None,  #May be set to None
  'COLLECTION': 'classic',
}

MONGO_ADSDATA = MONGO.copy()
MONGO_ADSDATA['DATABASE'] = 'adsdata'
MONGO_ADSDATA['COLLECTION'] = 'docs'
MONGO_ADSDATA['PORT'] = '27017'
MONGO_ADSDATA['USER'] = 'adsdata'
MONGO_ADSDATA['PASSWD'] = 'fake'


MONGO_ORCID = MONGO_ADSDATA.copy()
MONGO_ORCID['COLLECTION'] = 'orcid_claims'

#Order matches their priority
BIBCODE_FILES = [
  '/proj/ads/abstracts/ast/load/current/index.status',
  '/proj/ads/abstracts/phy/load/current/index.status',
  '/proj/ads/abstracts/gen/load/current/index.status',
  '/proj/ads/abstracts/pre/load/current/index.status',
]

BIBCODES_PER_JOB = 100

MERGER_RULES = {
  #<metadata type="general">
  'arxivcategories':      'takeAll',
  'keywords':             'takeAll',
  'titles':               'originTrustMerger',
  'abstracts':            'originTrustMerger',
  'authors':              'authorMerger',
  'publication':          'publicationMerger',
  'conf_metadata':        'originTrustMerger',
  'isbns':                'takeAll',
  'issns':                'takeAll',
  'doi':                  'originTrustMerger',
  'copyright':            'originTrustMerger',
  'comment':              'originTrustMerger',
  'pubnote':              'takeAll',
  'language':             'originTrustMerger',

  #<metadata type="properties">
  'databases':            'takeAll',
  'doctype':              'originTrustMerger',
  'bibgroups':            'takeAll',
  'openaccess':           'booleanMerger',
  'ads_openaccess':       'booleanMerger',
  'eprint_openaccess':    'booleanMerger',
  'pub_openaccess':       'booleanMerger',
  'private':              'originTrustMerger',
  'bibgroups':            'takeAll',
  'ocrabstract':          'booleanMerger',
  'private':              'booleanMerger',
  'refereed':             'booleanMerger',
  'associates':           'takeAll',
  'data_sources':         'takeAll',
  'vizier_tables':        'takeAll',

  #<metadata type="references">
  'references':           'referencesMerger',

  #<metadata type="relations">
  'preprints':            'takeAll',
  'alternates':           'takeAll',
  'links':                'takeAll',
}

_PRIORITIES_DEFAULT = {
  10: ['ADS METADATA',],
  1.0: ['ISI'],
  0.5: ['ASJ','A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN', 'ANREV', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'AUTHOR', 'OTHER', 'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE', 'JSTAGE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'IVOA', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC', 'JACOW', 'SARA',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOA', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ', 'RSOC', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SIF', 'SLO',
      'SOFIA', 'SPIE', 'SPIKA', 'SPITZER', 'SPRINGER', 'SPRN', 'STARD', 'STECF',
      'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SHA', 'SIGMA', 'SUNGE',
      'TELLUS', 'ZENODO','KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  0.49: ['PUBLISHER'],
  0.45: ['ARI', 'ARIBIB', 'JSTOR', 'KATKAT', 'AAA', ],
  0.4: ['CARL', 'CFA', 'HOLLIS', 'LIBRARY', 'POS', 'PRINCETON', 'SIMBAD', 'CDS',
      'STSCI', 'UTAL',],
  0.375: ['STI', 'WEB',],
  0.35: ['AP', 'CROSSREF', 'GCPD', 'GONG', 'KNUDSEN', 'METBASE',],
  0.3: ['OCR',],
  0.25: ['NED',],
  0.2: ['ARXIV',],
}

_PRIORITIES_JOURNALS = {
  10: ['ADS METADATA',],
  1.0: ['ISI'],
  0.5: ['ASJ','A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN', 'ANREV', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'AUTHOR', 'OTHER', 'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE', 'JSTAGE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'IVOA', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC', 'JACOW', 'SARA',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOA' 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ', 'RSOC', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SIF', 'SLO',
      'SOFIA', 'SPIE', 'SPIKA', 'SPITZER', 'SPRINGER', 'SPRN', 'STARD', 'STECF',
      'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SIGMA', 'SUNGE',
      'TELLUS', 'ZENODO','KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  0.49: ['PUBLISHER'],
  0.45: ['JSTOR','AAA',],
  0.4: ['CARL', 'CFA', 'HOLLIS', 'LIBRARY', 'POS', 'PRINCETON', 'SIMBAD', 'CDS',
      'STSCI', 'UTAL',],
  0.375: ['STI', 'WEB',],
  0.35: ['AP', 'CROSSREF', 'GCPD', 'GONG', 'METBASE',],
  0.3: ['OCR',],
  0.25: ['NED',],
  0.225: ['ARI', 'ARIBIB', 'KNUDSEN', 'KATKAT',],
  0.2: ['ARXIV',],
}

_PRIORITIES_AUTHORS = {
  10: ['ADS METADATA',],
  1.0: ['ISI'],
  0.5: ['ASJ','A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN', 'ANREV', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'AUTHOR', 'OTHER', 'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE', 'JSTAGE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'IVOA', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOA', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ',  'RSOC', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SIF', 'SLO', 'JACOW', 'SARA',
      'SOFIA', 'SPIE', 'SPIKA', 'SPITZER', 'SPRINGER', 'SPRN', 'STARD', 'STECF',
      'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SHA', 'SIGMA', 'SUNGE',
      'TELLUS', 'ZENODO','KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  0.49: ['PUBLISHER'],
  0.45: ['ARI', 'ARIBIB', 'JSTOR', 'KATKAT', 'AAA', ],
  0.4: ['CARL', 'CFA', 'HOLLIS', 'LIBRARY', 'POS', 'PRINCETON', 'SIMBAD', 'CDS',
      'STSCI', 'UTAL',],
  0.375: ['WEB',],
  0.35: ['AP', 'CROSSREF', 'GCPD', 'GONG', 'KNUDSEN', 'METBASE',],
  0.3: ['OCR',],
  0.25: ['NED',],
  0.225: ['STI',],
  0.2: ['ARXIV',],
}

_PRIORITIES_ABSTRACTS = {
  10: ['ADS METADATA',],
  1.0: ['ISI'],
  0.5: ['ASJ','A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN','ANREV', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'AUTHOR', 'OTHER', 'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE', 'JSTAGE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'IVOA', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC', 'JACOW','SARA',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOA', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ',  'RSOC', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SIF', 'SLO',
      'SOFIA', 'SPIE', 'SPIKA', 'SPITZER', 'SPRINGER', 'SPRN', 'STARD', 'STECF',
      'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SHA', 'SIGMA', 'SUNGE',
      'TELLUS', 'ZENODO','KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  0.49: ['PUBLISHER'],
  0.45: ['ARI', 'ARIBIB', 'JSTOR', 'KATKAT','AAA',],
  0.4: ['CARL', 'CFA', 'HOLLIS', 'LIBRARY', 'POS', 'PRINCETON', 'SIMBAD', 'CDS',
      'STSCI', 'UTAL',],
  0.375: ['WEB',],
  0.35: ['AP', 'CROSSREF', 'GCPD', 'GONG', 'KNUDSEN', 'METBASE',],
  0.3: ['OCR',],
  0.255:['ARXIV',],
  0.25: ['NED',],
  0.2: ['STI'],
}

_PRIORITIES_REFERENCES = {
  0: ['AUTHOR','ISI','OTHER'],
  9.1: ['SPRINGER',],
  9: ['ASJ','A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN','ANREV', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE', 'JSTAGE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'IVOA', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC', 'JACOW', 'SARA',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOA', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ', 'RSOC', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SIF', 'SLO',
      'SPIE', 'SPIKA', 'SPITZER', 'SPRN', 'STARD', 'STECF',
      'SOFIA', 'STSCI', 'SERAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE',
      'ARI', 'KATKAT', 'ARIBIB', 'JSTOR', 'CARL', 'CFA', 'HOLLIS', 'LIBRARY',
      'POS', 'PRINCETON', 'SIMBAD', 'CDS','UTAL', 'STI', 'WEB',
      'AP', 'GCPD', 'GONG', 'KNUDSEN', 'METBASE', 'NED', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SHA', 'SIGMA', 'SUNGE',
      'TELLUS', 'ZENODO','KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  8.9: ['PUBLISHER'],
  8.5: ['OCR', 'ADS METADATA'],
  8: ['CROSSREF',],
  5: ['ARXIV',],
  4.5: ['AAA'],
}

PRIORITIES = {
  'default': dict((source, score)
    for score, sources in _PRIORITIES_DEFAULT.iteritems()
    for source in sources),
  'journals': dict((source, score)
    for score, sources in _PRIORITIES_JOURNALS.iteritems()
    for source in sources),
  'authors': dict((source, score)
    for score, sources in _PRIORITIES_AUTHORS.iteritems()
    for source in sources),
  'references': dict((source, score)
    for score, sources in _PRIORITIES_REFERENCES.iteritems()
    for source in sources),
  'abstracts': dict((source, score)
    for score, sources in _PRIORITIES_ABSTRACTS.iteritems()
    for source in sources),
}



#References with these origins will always be added to merged reference metadata blocks.
REFERENCES_ALWAYS_APPEND = ['ISI', 'AUTHOR', 'OTHER',]
