from itertools import count

from asamended.uscode.node import Node, fromdata
from asamended.uscode.ident import Ident, IdentSet

from tater.ext.visitors import DataVisitor


class IdentAccumulator(DataVisitor):
    '''For visiting search results and gathering all the ids.
    '''
    def __init__(self):
        self.ids = []

    def visit_str(self, obj):
        if obj.startswith('/us/usc'):
            self.ids.append(Ident(obj))

    visit_unicode = visit_str

    def finalize(self):
        return IdentSet(self.ids)


class SearchResult(dict):

    def __init__(self, client, *args, **kwargs):
        super(SearchResult, self).__init__(*args, **kwargs)
        self.client = client

    def get_ids(self):
        for result in self['results']:
            yield result['ident']

    def iternodes(self):
        from asamended.uscode import ancestors
        return ancestors(self.get_ids())
