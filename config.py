import os
import sys

SOLR_URLS=[
  'http://localhost:9983/solr/BumblebeeETL/update'
]

#SQLALCHEMY_URL = 'sqlite:///'
SQLALCHEMY_URL = 'postgres://user:password@localhost:15432/import_pipeline'
SQLALCHEMY_ECHO = False

CELERY_INCLUDE = ['aip.tasks']
CELERY_BROKER = 'pyamqp://user:password@localhost:6672/import_pipeline'
OUTPUT_CELERY_BROKER = 'pyamqp://user:password@localhost:5682/master_pipeline'
OUTPUT_TASKNAME = 'adsmp.tasks.task_update_record'

# when running locally
# SQLALCHEMY_URL = 'postgres://docker:docker@localhost:6432/docker' #'sqlite:///test.db'
# CELERY_BROKER = 'pyamqp://guest:guest@localhost:6672/import_pipeline'




#Order matches their priority
BIBCODE_FILES = [
    './logs/input/current/ast/load/current/index.status',
    './logs/input/current/phy/load/current/index.status',
    './logs/input/current/gen/load/current/index.status',
    './logs/input/current/pre/load/current/index.status',
]

BIBCODES_PER_JOB = 100


# ================= celery/rabbitmq rules============== #
# ##################################################### #

ACKS_LATE=True
PREFETCH_MULTIPLIER=1
CELERYD_TASK_SOFT_TIME_LIMIT = 120




# ================= merger rules ====================== #
# ##################################################### #

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
  'series':               'originTrustMerger',

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
  'identifiers':          'takeAll',
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
  0.6: ['STI'],
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
  0.375: ['AP', 'METBASE', 'WEB',],
  0.35: ['CROSSREF', 'GCPD', 'GONG', 'KNUDSEN'],
  0.3: ['OCR',],
  0.25: ['NED',],
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


# Direct Ingest Defaults

## ================ ArXiv data location ================ #
## ##################################################### #
# Where the worker is going to look for incoming ArXiv
# submissions: ARCHIVE_ABS_DIR

ARXIV_INCOMING_ABS_DIR = '/proj/ads/abstracts/sources/ArXiv'
ARXIV_INCOMING_ABS_CONSIDER_ONLY_NEW = True # By default, ignore updates to avoid bibcode resurection problems


## ================ APS data location ================== #
## ##################################################### #
# Where the worker is going to look for incoming APS
# submissions:

APS_UPDATE_AGENT_LOG = '/proj/ads/abstracts/sources/APS/logs/aps-update.out.'
