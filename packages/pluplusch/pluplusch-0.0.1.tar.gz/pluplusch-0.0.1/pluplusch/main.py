from pickle_warehouse import Warehouse
from picklecache import downloader
import requests

import pluplusch.index as i
 

def pluplusch(catalogs = None, cache_dir = '.pluplusch', proxies = {}):

    _get = downloader(lambda url: requests.get(url, proxies = proxies), Warehouse(cache_dir, mutable = False))
    def get(url):
        response = _get(url)
        if response.ok:
            return response
        else:
            raise ValueError('%d response at %s' % (response.status_code, url))

    submodules = i.submodules()

    if catalogs == None:
        # Use all catalogs.
        catalogs = list(i.all_catalogs())

    for catalog in catalogs:
        software = i.catalog_to_software(catalog)
        yield from getattr(submodules[software], 'download')(get, catalog)
