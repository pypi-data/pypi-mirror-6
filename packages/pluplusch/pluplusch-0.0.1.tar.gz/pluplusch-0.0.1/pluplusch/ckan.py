import json
import functools, itertools
from urllib.parse import urljoin

catalogs = [
    'http://datahub.io',
    'http://opendata.comune.bari.it',
    'http://africaopendata.org',
    'http://opendata.aragon.es',
    'http://daten.berlin.de',
    'http://data.buenosaires.gob.ar',
    'http://ie.ckan.net',
    'http://it.ckan.net',
    'http://rs.ckan.net',
    'http://br.ckan.net',
    'http://datos.codeandomexico.org',
    'http://cz.ckan.net',
    'http://dados.gov.br',
    'http://dadosabertos.senado.gov.br',
    'http://dados.novohamburgo.rs.gov.br',
    'http://data.gv.at',
    'http://data.linz.gv.at',
    'http://fi.thedatahub.org',
    'http://data.sa.gov.au',
    'http://www.data.gc.ca',
    'http://data.gov.sk',
    'http://data.gov.uk',
    'http://data.qld.gov.au',
    'http://data.openpolice.ru',
    'http://datacatalogs.org',
    'http://www.datagm.org.uk',
    'http://datakilder.no',
    'http://datospublicos.org',
    'http://data.denvergov.org',
    'http://ckan.emap.fgv.br',
    'http://open-data.europa.eu',
    'http://www.healthdata.gov',
    'http://www.hri.fi',
    'http://data.graz.gv.at',
    'http://daten.hamburg.de',
    'http://data.codeforhouston.com',
    'http://iatiregistry.org',
    'http://data.klp.org.in',
    'http://thedatahub.kr',
    'http://www.nosdonnees.fr',
    'http://offenedaten.de',
    'http://data.opencolorado.org',
    'http://catalog.opendata.in.th',
    'http://www.opendatahub.it',
    'http://dati.trentino.it',
    'http://data.openva.com',
    'http://www.opendata-hro.de',
    'http://opengov.es',
    'http://data.ottawa.ca',
    'http://data.overheid.nl',
    'http://www.opendata.provincia.roma.it',
    'http://publicdata.eu',
    'http://www.daten.rlp.de',
    'http://www.rotterdamopendata.nl',
    'http://data.cityofsantacruz.com',
    'http://thedatahub.org',
    'http://dati.toscana.it',
]

def dataset_ids(get, catalog, page):
    url = urljoin(catalog, '/api/search/dataset?q=&start=%d' % page)
    response = get(url)
    data = json.loads(response.text)
    return data['results']

def dataset(get, catalog, datasetid):
    url = urljoin(catalog, '/api/rest/dataset/%s' % datasetid)
    response = get(url)
    dataset = json.loads(response.text)
    dataset['catalog'] = catalog
    return dataset

def download(get, catalog):
    dataset_ids_page = functools.partial(dataset_ids, get, catalog)
    for page in itertools.count(1):
        result = dataset_ids_page(page)
        if result == []:
            break
        else:
            for dataset_id in result:
                yield dataset(get, catalog, dataset_id)
