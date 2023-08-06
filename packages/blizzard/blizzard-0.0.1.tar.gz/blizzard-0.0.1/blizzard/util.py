import os
from logging import getLogger

import requests
import pickle_warehouse

logger = getLogger('blizzard')

def _get(datadir:str, url:str):
    warehouse = pickle_warehouse.Warehouse(datadir)
    if url in warehouse:
        logger.debug('%s: Loading from cache' % url)
        response = warehouse[url]

        # Clear bad files
        if not response.ok:
            logger.error('%s: %d in cached response' % (url, response.status_code))
            del(warehouse[url])
            return _get(datadir, url)
    else:
        if 'http_proxy' in os.environ:
            logger.info('Proxy: %s' % os.environ['http_proxy'])
            proxies = {'http_proxy': os.environ['http_proxy']}
        else:
            logger.info('Proxy: No proxy')
            proxies = {}

        logger.debug('%s: Downloading with proxies %s' % (url,proxies))
        response = requests.get(url, proxies = proxies)

        # Stop on bad files
        if not response.ok:
            logger.error('%s: %d in new response' % (url, response.status_code))
            logger.error('%s: %s' % (url, response.text))
            raise ValueError('Bad HTTP response')

        warehouse[url] = response

    return response

def ignore(dataset):
    if 'geo_shape' in set(f['type'] for f in dataset['fields']):
        # csv parser can't handle geo data
        return True
    elif not dataset['download'].ok:
        # bad status code
        return True
    elif dataset['download'].text.strip() == '':
        # empty file
        return True
    else:
        return False
