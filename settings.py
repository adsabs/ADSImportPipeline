import os
import sys

PROJECT_HOME = os.path.abspath(os.path.dirname(__file__))

# CLASSIC_BIBCODES = {
#   'AST': '/proj/ads/abstracts/ast/load/current/index.status',
#   'PHY': '/proj/ads/abstracts/phy/load/current/index.status',
#   'GEN': '/proj/ads/abstracts/gen/load/current/index.status',
#   'PRE': '/proj/ads/abstracts/pre/load/current/index.status',
# }
# CLASSIC_BIBCODES = {
#   'AST': 'ast.txt',
# }
CLASSIC_BIBCODES = {}

BIBCODES_PER_JOB = 200

MONGO = {
  'HOST': os.environ.get('MONGO_HOST','localhost'),
  'PORT': os.environ.get('MONGO_PORT',27017),
  'DATABASE': os.environ.get('MONGO_DATABASE','ads'),
  'USER': None,    #May be set to None
  'PASSWD': None,  #May be set to None
  'COLLECTION': 'classic',
}

MERGER_RULES = {
  'default':              'stringConcatenateMerger',

  #<metadata type="general">
  'arxivcategories':      'originTrustMerger',
  'keywords':             'takeAll',
  'titles':               'originTrustMerger',
  'abstracts':            'originTrustMerger',
  'authors':              'authorMerger',
  'publication':          'publicationMerger',
  'conf_metadata':        'originTrustMerger',
  'dates':                'originTrustMerger',
  'isbns':                'takeAll',
  'issns':                'takeAll',
  'doi':                  'originTrustMerger',
  'copyright':            'originTrustMerger',
  'comment':              'originTrustMerger',
  'pubnote':              'takeAll',

  #<metadata type="properties">
  'databases':            'takeAll',
  'pubtype':              'originTrustMerger',
  'bibgroups':            'takeAll',
  'openaccess':           'booleanMerger',
  'private':              'originTrustMerger',
  'bibgroups':            'takeAll',
  'nonarticle':           'booleanMerger',
  'ocrabstract':          'booleanMerger',
  'private':              'booleanMerger',
  'refereed':             'booleanMerger',
  'associates':           'takeAll',

  #<metadata type="references">
  'references':            'referencesMerger',

  #<metadata type="relations">
  'preprints':           'takeAll',
  'alternates':           'takeAll',
  'links':                'takeAll',
}

__PRIORITIES_DEFAULT = {
  10: ['ADS METADATA',],
  1.0: ['ISI'],
  0.5: ['A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'AUTHOR', 'OTHER', 'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SLO',
      'SPIE', 'SPIKA', 'SPITZER', 'SPRINGER', 'SPRN', 'STARD', 'STECF',
      'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SHA', 'SIGMA', 'SUNGE',
      'TELLUS', 'KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  0.49: ['PUBLISHER'],
  0.45: ['ARI', 'ARIBIB', 'JSTOR', 'KATKAT',],
  0.4: ['CARL', 'CFA', 'HOLLIS', 'LIBRARY', 'POS', 'PRINCETON', 'SIMBAD', 'CDS',
      'STSCI', 'UTAL',],
  0.375: ['STI', 'WEB',],
  0.35: ['AP', 'CROSSREF', 'GCPD', 'GONG', 'KNUDSEN', 'METBASE',],
  0.3: ['OCR',],
  0.25: ['NED',],
  0.2: ['ARXIV',],
}

__PRIORITIES_JOURNALS = {
  10: ['ADS METADATA',],
  1.0: ['ISI'],
  0.5: ['A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'AUTHOR', 'OTHER', 'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SLO',
      'SPIE', 'SPIKA', 'SPITZER', 'SPRINGER', 'SPRN', 'STARD', 'STECF',
      'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SIGMA', 'SUNGE',
      'TELLUS', 'KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  0.49: ['PUBLISHER'],
  0.45: ['JSTOR',],
  0.4: ['CARL', 'CFA', 'HOLLIS', 'LIBRARY', 'POS', 'PRINCETON', 'SIMBAD', 'CDS',
      'STSCI', 'UTAL',],
  0.375: ['STI', 'WEB',],
  0.35: ['AP', 'CROSSREF', 'GCPD', 'GONG', 'METBASE',],
  0.3: ['OCR',],
  0.25: ['NED',],
  0.225: ['ARI', 'ARIBIB', 'KNUDSEN', 'KATKAT',],
  0.2: ['ARXIV',],
}

__PRIORITIES_AUTHORS = {
  10: ['ADS METADATA',],
  1.0: ['ISI'],
  0.5: ['A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'AUTHOR', 'OTHER', 'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SLO',
      'SPIE', 'SPIKA', 'SPITZER', 'SPRINGER', 'SPRN', 'STARD', 'STECF',
      'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SHA', 'SIGMA', 'SUNGE',
      'TELLUS', 'KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  0.49: ['PUBLISHER'],
  0.45: ['ARI', 'ARIBIB', 'JSTOR', 'KATKAT',],
  0.4: ['CARL', 'CFA', 'HOLLIS', 'LIBRARY', 'POS', 'PRINCETON', 'SIMBAD', 'CDS',
      'STSCI', 'UTAL',],
  0.375: ['WEB',],
  0.35: ['AP', 'CROSSREF', 'GCPD', 'GONG', 'KNUDSEN', 'METBASE',],
  0.3: ['OCR',],
  0.25: ['NED',],
  0.225: ['STI',],
  0.2: ['ARXIV',],
}

__PRIORITIES_ABSTRACTS = {
  10: ['ADS METADATA',],
  1.0: ['ISI'],
  0.5: ['A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'AUTHOR', 'OTHER', 'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SLO',
      'SPIE', 'SPIKA', 'SPITZER', 'SPRINGER', 'SPRN', 'STARD', 'STECF',
      'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SHA', 'SIGMA', 'SUNGE',
      'TELLUS', 'KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  0.49: ['PUBLISHER'],
  0.45: ['ARI', 'ARIBIB', 'JSTOR', 'KATKAT',],
  0.4: ['CARL', 'CFA', 'HOLLIS', 'LIBRARY', 'POS', 'PRINCETON', 'SIMBAD', 'CDS',
      'STSCI', 'UTAL',],
  0.375: ['WEB',],
  0.35: ['AP', 'CROSSREF', 'GCPD', 'GONG', 'KNUDSEN', 'METBASE',],
  0.3: ['OCR',],
  0.255:['ARXIV',],
  0.25: ['NED',],
  0.2: ['STI'],
}

__PRIORITIES_REFERENCES = {
  10: ['AUTHOR',],
  9.5: ['ISI',],
  9.1: ['SPRINGER',],
  9.05:['OTHER',],
  9: ['A&A', 'A&AS', 'A&G', 'AAO', 'AAS', 'AASP', 'AAVSO', 'ACA',
      'ACASN', 'ACHA', 'ACTA', 'ADASS', 'ADIL', 'ADS', 'AFRSK', 'AG',
      'AGDP', 'AGU', 'AIP', 'AJ', 'ALMA', 'AMS', 'AN', 'ANRFM', 'ANRMS',
      'APJ', 'APS', 'ARA&A', 'ARAA', 'ARAC', 'AREPS', 'ARNPS', 'ASBIO',
      'ASD', 'ASL', 'ASP', 'ASPC', 'ASTL', 'ASTRON', 'ATEL', 'ATSIR',
      'BAAA', 'BAAS', 'BALTA', 'BASBR', 'BASI', 'BAVSR', 'BEO',
      'BESN', 'BLAZ', 'BLGAJ', 'BOTT', 'BSSAS', 'CAPJ', 'CBAT', 'CDC',
      'CEAB', 'CFHT', 'CHAA', 'CHANDRA', 'CHJAA', 'CIEL', 'COAST',
      'COPERNICUS', 'COSKA', 'CSCI', 'CUP', 'CXC', 'CXO', 'DSSN',
      'E&PSL', 'EDP', 'EDP SCIENCES', 'KONKOLY', 'EJTP', 'ELSEVIER', 'ESA', 'ESO', 'ESP', 'EUVE',
      'FCPH', 'FUSE', 'GCN', 'GJI', 'GRG', 'HISSC', 'HST', 'HVAR', 'IAJ',
      'IAU', 'IAUC', 'IAUDS', 'IBVS', 'ICAR', 'ICQ', 'IMO', 'INGTN',
      'IOP', 'ISAS', 'ISSI', 'IUE', 'JAA', 'JAD', 'JAHH', 'JAPA', 'JASS',
      'JAVSO', 'JBAA', 'JENAM', 'JHA', 'JIMO', 'JKAS', 'JPSJ', 'JRASC',
      'JSARA', 'JST', 'KFNT', 'KITP', 'KLUWER', 'KOBV', 'KON', 'LNP',
      'LOC', 'LPI', 'LRR', 'LRSP', 'M&PS', 'M+PS', 'METIC', 'MIT',
      'MNRAS', 'MNSSA', 'MOLDAVIA', 'MPBU', 'MPC', 'MPE', 'MPSA',
      'MmSAI', 'NAS', 'NATURE', 'NCSA', 'NEWA', 'NOAO', 'NRAO', 'NSTED',
      'O+T', 'OAP', 'OBS', 'OEJV', 'OSA', 'PABEI', 'PADEU', 'PAICU',
      'PAICz', 'PAOB', 'PASA', 'PASJ', 'PASP', 'PDS', 'PHIJA', 'PHYS',
      'PJAB', 'PKAS', 'PLR', 'PNAS', 'POBEO', 'PSRD', 'PTP', 'PZP',
      'QJRAS', 'RMXAA', 'RMXAC', 'ROAJ', 'RVMA', 'S&T', 'SABER', 'SAI',
      'SAJ', 'SAO', 'SAS', 'SCI', 'SCIENCE', 'SERB', 'SF2A', 'SLO',
      'SPIE', 'SPIKA', 'SPITZER', 'SPRN', 'STARD', 'STECF',
      'STSCI', 'SerAJ', 'T+F', 'TERRAPUB', 'UCP', 'UMI', 'USCI', 'USNO',
      'VATICAN', 'VERSITA', 'WGN', 'WILEY', 'WSPC', 'XMM', 'XTE',
      'ARI', 'KATKAT', 'ARIBIB', 'JSTOR', 'CARL', 'CFA', 'HOLLIS', 'LIBRARY',
      'POS', 'PRINCETON', 'SIMBAD', 'CDS','UTAL', 'STI', 'WEB',
      'AP', 'GCPD', 'GONG', 'KNUDSEN', 'METBASE', 'NED', 'BLACKWELL',
      'AFOEV', 'ASCL', 'ATNF', 'CJAA', 'CONF', 'EDITOR', 'EGU', 'ELIBRARY', 'IPAP',
      'JDSO', 'LPI', 'MMSAI', 'NCIM', 'PAICZ', 'RSPSA', 'SERAJ', 'SHA', 'SIGMA', 'SUNGE',
      'TELLUS', 'KONKOLY OBSERVATORY',
      'ARPC', 'ANNREV', 'ARMS', 'CSIRO', 'RSC', 'JON', 'JBIS','OUP', 'CSP',
      'DE GRUYTER', 'PASRB', 'BUEOP', 'EAAS', 'AZAJ'],
  8.9: ['PUBLISHER'],
  8.5: ['OCR', 'ADS METADATA'],
  8: ['CROSSREF',],
  5: ['ARXIV',],
}

PRIORITIES = {
  'default': dict((source, score)
    for score, sources in __PRIORITIES_DEFAULT.iteritems()
    for source in sources),
  'journals': dict((source, score)
    for score, sources in __PRIORITIES_JOURNALS.iteritems()
    for source in sources),
  'canonical_journals': dict((source, score)
    for score, sources in __PRIORITIES_JOURNALS.iteritems()
    for source in sources),
  'authors': dict((source, score)
    for score, sources in __PRIORITIES_AUTHORS.iteritems()
    for source in sources),
  'references': dict((source, score)
    for score, sources in __PRIORITIES_REFERENCES.iteritems()
    for source in sources),
  'abstracts': dict((source, score)
    for score, sources in __PRIORITIES_ABSTRACTS.iteritems()
    for source in sources),
}



#References with these origins will always be added to merged reference metadata blocks.
REFERENCES_ALWAYS_APPEND = ['ISI', 'AUTHOR', 'OTHER', 'CROSSREF']