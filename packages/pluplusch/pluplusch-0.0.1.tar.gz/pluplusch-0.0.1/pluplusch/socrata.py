import json
import functools
import itertools
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

catalogs = [
    'https://data.colorado.gov',
    'https://data.nola.gov',
    'https://healthmeasures.aspe.hhs.gov',
    'https://data.cityofchicago.org',
    'https://data.wa.gov',
    'https://opendata.go.ke',
    'https://data.austintexas.gov',
    'https://data.cityofnewyork.us',
    'https://info.samhsa.gov',
    'https://data.taxpayer.net',
    'https://data.cityofmadison.com',
    'https://data.slcgov.com',
    'https://data.illinois.gov',
    'https://data.somervillema.gov',
    'https://iranhumanrights.socrata.com',
    'https://data.hawaii.gov',
    'https://data.maryland.gov',
    'https://data.ny.gov',
    'https://data.mo.gov',
    'https://data.nfpa.org',
    'https://nmfs.socrata.com',
    'https://data.govloop.com',
    'https://data.sunlightlabs.com',
    'https://electionsdata.kingcounty.gov',
    'https://data.undp.org',
    'https://deleon.socrata.com',
    'https://data.energystar.gov',
    'https://explore.data.gov',
    'https://data.weatherfordtx.gov',
    'https://bronx.lehman.cuny.edu',
    'https://data.sfgov.org',
    'https://data.edmonton.ca',
    'https://data.consumerfinance.gov',
    'https://www.metrochicagodata.org',
    'https://data.kingcounty.gov',
    'https://data.baltimorecity.gov',
    'https://health.data.ny.gov',
    'https://dati.lombardia.it',
    'https://datacatalog.cookcountyil.gov',
    'https://www.opendatanyc.com',
    'https://cookcounty.socrata.com',
    'https://data.oregon.gov',
    'https://data.oaklandnet.com',
    'https://data.raleighnc.gov',
    'https://finances.worldbank.org',
    'https://data.honolulu.gov',
    'https://opendata.socrata.com',
    'https://data.cityofboston.gov',
    'https://data.ok.gov',
    'https://data.cms.gov',
    'https://data.snostat.org',
    'https://www.halifaxopendata.ca',
    'https://data.wellingtonfl.gov',
    'https://gettingpastgo.socrata.com',
    'https://www.data.act.gov.au',
    'https://data.redmond.gov',
    'https://data.seattle.gov',
    'https://data.montgomerycountymd.gov',
    'https://data.acgov.org',
    'https://data.medicare.gov'
]

def page(get, domain_with_scheme, page_number):
    full_url = urljoin(domain_with_scheme, '/api/views?page=%d' % page_number)
    response = get(full_url)
    search_results = json.loads(response.text)
    return search_results

def download(get, domain):
    pages = (page(get, domain, page_number) for page_number in itertools.count(1))
    for search_results in itertools.takewhile(lambda x: x != [], pages):
        yield from search_results
