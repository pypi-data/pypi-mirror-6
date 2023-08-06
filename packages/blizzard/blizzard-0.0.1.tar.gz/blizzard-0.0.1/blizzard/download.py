from concurrent.futures import ThreadPoolExecutor
from functools import partial
import json

catalogs = [
    'http://data.iledefrance.fr',
    'http://opendata.paris.fr.opendatasoft.com',
    'http://tourisme04.opendatasoft.com',
    'http://tourisme62.opendatasoft.com',
    'http://grandnancy.opendatasoft.com',
    'http://bistrotdepays.opendatasoft.com',
    'http://scisf.opendatasoft.com',
    'http://pod.opendatasoft.com',
    'http://dataratp.opendatasoft.com',
    'http://public.opendatasoft.com',
    'http://ressources.data.sncf.com',
]

def datasets(get, catalog):
    # Search an OpenDataSoft portal, and add things.
    # I chose OpenDataSoft because they care a lot about metadata.
    response = get(catalog + '/api/datasets/1.0/search?rows=1000000')
    result = json.loads(response.text)['datasets']
    for r in result:
        r['catalog'] = catalog
    return result

def download(get, catalog, datasetid):
    url = '%s/explore/dataset/%s/download/?format=csv' % (catalog, datasetid)
    response = get(url)
    if not response.ok:
        logger.error('url: %d status code' % response.status_code)
    return response

def _run(get, catalog):
    n = 30
    def f(dataset):
        dataset['download'] = download(get, catalog, dataset['datasetid'])
        return dataset
    with ThreadPoolExecutor(n) as e:
        yield from e.map(f, datasets(get,catalog))

def all(get):
    with ThreadPoolExecutor(len(catalogs)) as e:
        for x in e.map(partial(_run, get),catalogs):
            yield from x
