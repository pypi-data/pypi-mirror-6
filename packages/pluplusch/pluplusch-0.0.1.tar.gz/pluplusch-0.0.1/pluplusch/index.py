from importlib import import_module

softwares = ['azavea','ckan','junar','opendatasoft','socrata']

def submodules(softwares = softwares):
    return {software: import_module('pluplusch.%s' % software) for software in softwares}

def catalogs(submodules = submodules(softwares)):
    for software, module in submodules.items():
        for catalog in getattr(module, 'catalogs'):
            yield catalog, software

def catalog_to_software(catalog, lookup = {}):
    if lookup == {}:
        lookup.update(catalogs(submodules(softwares)))

    if catalog in lookup:
        return lookup[catalog]
    else:
        if catalog.startswith('http'):
            msg = "I don't know the software that \"%s\" uses." % catalog
        else:
            msg = "I don't know \"%s\"; try adding \"https://\" or \"http://\" in front of the URL." % catalog
        raise ValueError(msg)

def all_catalogs():
    for catalog, software in catalogs(submodules(softwares)):
        yield catalog
