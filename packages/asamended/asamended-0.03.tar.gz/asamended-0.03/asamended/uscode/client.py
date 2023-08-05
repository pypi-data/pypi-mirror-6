import os
import urllib
import urlparse

import requests

from tater.utils import CachedAttr

from asamended.config import logging
from asamended.uscode.search import SearchResult


class UserKeyRequired(Exception):
    pass


class Client(object):

    def __init__(self,
            user_key=None, version_str='v1',
            root='http://asamended.com/'):

        self.root = root
        self.version_str = version_str

        # Store the user_key.
        if user_key is None:
            user_key = os.environ.get('ASAMENDED_USER_KEY')
        if user_key is None:
            raise UserKeyRequired()
        self.user_key = user_key

        self.logger = logging.getLogger('asamended.uscode.client')

    def get_url(self, url, **params):
        '''Adds user_token to url and GETs it.
        '''
        params.update(user_key=self.user_key)
        self.logger.info('API Call: [GET] %s %r' % (url, params))
        resp = requests.get(url, params=params)
        extra = dict(url=resp.url, method='GET', status=resp.status_code)
        self.logger.info('... status: %s %s' % (resp.status_code, resp.url))
        return resp

    def get_resource(self, resource_name, **params):
        rel_url = self.resources[resource_name]
        url = urlparse.urljoin(self.root, rel_url)
        return self.get_url(url, **params)

    @CachedAttr
    def resources(self):
        '''Should use reverse internally.
        '''
        parts = (self.root, 'api/%s/resources' % self.version_str)
        url = urlparse.urljoin(*parts)
        return self.get_url(url).json()['response']

    # -----------------------------------------------------------------------
    # Public methods.
    # -----------------------------------------------------------------------
    def descendants(self, ident, max_depth=None, **params):
        return self.get_resource(
            'descendants', ident=ident, max_depth=max_depth, **params).json()

    def descendants_only(self, ident, max_depth=None, **params):
        return self.get_resource(
            'descendants_only', ident=ident, max_depth=max_depth, **params).json()

    def ancestors(self, ident, **params):
        return self.get_resource('ancestors', ident=ident, **params).json()

    def search(self, **params):
        facet = params.get('facet')
        if facet is not None:
            if isinstance(facet, (list, tuple)):
                params['facet'] = ','.join(facet)
        results = self.get_resource('search', **params).json()
        return SearchResult(self, results)

    def search_iter(self, **params):
        facet = params.get('facet')
        if facet is not None:
            if isinstance(facet, (list, tuple)):
                params['facet'] = ','.join(facet)
        results = self.get_resource('search', **params).json()
        yield SearchResult(self, results)
        for page in range(int(results['meta']['pages'])):
            results = self.get_resource('search', page=page, **params).json()
            yield SearchResult(self, results)


client = Client()


if __name__ == '__main__':
    x = Client()#root='http://localhost:8000')
    x.resources
    x.descendants(ident='/us/usc/t26', max_depth=1)
    x.ancestors(ident="/us/usc/t26")

    import pdb; pdb.set_trace()