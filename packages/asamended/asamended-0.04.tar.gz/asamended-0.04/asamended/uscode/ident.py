import re
from functools import partial
from itertools import count
from operator import itemgetter

import networkx as nx
from tater.utils import CachedAttr

from asamended.utils import OrderedSet


class Ident(object):
    '''This class provides methods for analyzing the (excellent)
    ident fields in the US Code data.
    '''
    tagdict = dict(
        t='title',
        st='subtitle',
        ch='chapter',
        sch='subchapter',
        p='part',
        sp='subpart',
        a='article',
        sa='subarticle',
        s='section')

    def __init__(self, ident):
        self.ident = ident

    @CachedAttr
    def normalized(self):
        ident = self.ident.rstrip('/')
        if not ident.startswith('/'):
            ident = '/' + ident
        else:
            ident = ident
        return ident

    def _get_segments(self):
        counter = count()
        segments = self.normalized.split('/')
        for i in range(len(segments)):
            seg = '/'.join(segments[:(i + 1)])
            if not seg:
                continue
            yield next(counter), seg

    @CachedAttr
    def segments(self):
        '''Return a list like [
            '/us', '/us/usc', '/us/usc/t26', '/us/usc/t26/stE']
        '''
        return OrderedSet(self._get_segments())

    def __contains__(self, other):
        '''This is slightly magical, but defensible from
        a set/network theory standpoint.

        >>> from asamended.uscode.ident import Ident
        >>> x = Ident('/us/usc/t25/s123')
        >>> y = Ident('/us/usc/t25')
        >>> x in y
        '''
        return self.segments.issubset(other.segments)

    def bigtag(self):
        '''Return the guessed tag if the node is a "big" node.
        '''
        _, _, last = self.normalized.rpartition('/')
        chars = re.match(r'[^\d]+', last)
        if chars is None:
            raise ValueError('Unexpected ident: %r' % self.normalized)
        elif chars.group() in self.tagdict:
            return self.tagdict[chars.group()]
        else:
            return

    def is_section(self):
        return self.bigtag() == 'section'

    def __repr__(self):
        return 'Ident(%r)' % self.normalized

    def __unicode__(self):
        '''I sure hope you know what you're doing Thom.
        '''
        return self.normalized


class IdentSet(object):
    '''This class provides methods for analyzing sets of US Code IDs
    as a group.
    '''
    def __init__(self, ids, *more_ids):
        ids = list(ids)
        ids.extend(list(more_ids))
        self.ids = ids

    def to_digraph(self):
        '''Assemble these IDs into a DiGraph. The idea is only to build
        a good-enough graph to find the leaf nodes. We can get their
        full ancestry from the database.
        '''
        G = nx.DiGraph()

        for ident in self.ids:
            segments = ident.segments.sorted()[::-1]
            order, outbound = segments.pop()
            while segments:
                order, segment = segments.pop()
                inbound = segment
                G.add_edge(outbound, inbound)
                outbound = inbound
        return G

    def get_leaf_ids(self):
        outdegree = nx.out_degree_centrality(self.to_digraph())
        ids = filter(lambda id: not outdegree.get(id), outdegree)

        # Temporary hack to remove content path segments.
        scrub = partial(re.sub, r'/text\d+', '')
        ids = map(scrub, ids)
        return ids

    def __iter__(self):
        return iter(self.ids)


if __name__ == '__main__':

    ids = IdentSet(map(Ident, [
        "/us/usc/t7/s1635e",
        "/us/usc/t7/s1635d",
        "/us/usc/t7/s1446",
        "/us/usc/t7/s1471",
        "/us/usc/t7/s1631",
        "/us/usc/t7/s2906",
        "/us/usc/t7/s2902",
        "/us/usc/t7/s2904",
        "/us/usc/t7/s2905",
        "/us/usc/t7/s1636d",
        "/us/usc/t7/s5925",
        "/us/usc/t21/s616",
        "/us/usc/t21/s610",
        "/us/usc/t21/s321",
        "/us/usc/t21/s672",
        "/us/usc/t21/s673",
        "/us/usc/t21/s679",
        "/us/usc/t21/s693",
        "/us/usc/t21/s623",
        "/us/usc/t21/s620",
        "/us/usc/t21/s624",
        "/us/usc/t21/s601",
        "/us/usc/t21/s603",
        "/us/usc/t21/s661",
        "/us/usc/t21/s644",
        "/us/usc/t21/s641",
        "/us/usc/t21/s643",
        "/us/usc/t21/s642",
        "/us/usc/t12/s84",
        "/us/usc/t12/s1150a",
        "/us/usc/t16/s272c",
        "/us/usc/t16/s1244",
        "/us/usc/t16/s450y\u20133",
        "/us/usc/t16/s698u\u20133",
        "/us/usc/t16/s698u\u20135",
        "/us/usc/t16/s273c",
        "/us/usc/t16/s410hhh\u20137",
        "/us/usc/t19/s2497",
        "/us/usc/t18/s2311",
        "/us/usc/t18/s1857"]))

    # G = ids.to_digraph()
    x = ids.get_leaf_nodes()
    import pdb; pdb.set_trace()