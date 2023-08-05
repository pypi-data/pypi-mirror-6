from asamended.uscode.ident import IdentSet
from asamended.uscode.node import fromdata
from asamended.uscode.client import client
from asamended.uscode.search import SearchResult


def descendants(ident=None, *args, **kwargs):
    '''Get descendants and ancestors for the specified ident.
    '''
    ident = ident or '/us/usc'
    data = client.descendants(ident, *args, **kwargs)
    hydrated = fromdata(data)
    ident_node = hydrated.find().filter(ident=ident).next()
    return ident_node


def descendants_only(ident=None, *args, **kwargs):
    '''Get descendants for the specified ident.
    '''
    ident = ident or '/us/usc'
    data = client.descendants_only(ident, *args, **kwargs)
    hydrated = fromdata(data)
    ident_node = tree.find().filter(ident=ident).next()
    return ident_node


def ancestors(ident, *args, **kwargs):
    '''Get ancestors for the specified ident.
    '''
    listy_ident = None

    # Handle one or more string ids, joined with commas.
    if isinstance(ident, basestring):
        stringy_ident = ident
        if ',' in ident:
            listy_ident = ident.split(',')

    # Handle IdentSet.
    elif isinstance(ident, IdentSet):
        ident = list(ident)
        listy_ident = [i.normalized for i in ident]
        stringy_ident = ','.join(listy_ident)

    # Handle iterable.
    else:
        listy_ident = list(ident)
        stringy_ident = ','.join(listy_ident)

    data = client.ancestors(stringy_ident, *args, **kwargs)
    hydrated = fromdata(data)

    if listy_ident is not None:
        return hydrated.find().filter(ident__in=listy_ident)
    else:
        return hydrated.find().filter(ident=stringy_ident)


def search(*args, **kwargs):
    '''Get ancestors for the specified ident.
    '''
    data = client.search(*args, **kwargs)
    return SearchResult(client, data)
