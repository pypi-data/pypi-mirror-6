from operator import itemgetter

import networkx as nx

from tater import Node, NodeList, Visitor


class DiGraphRenderer(Visitor):

    def __init__(self):
        self.G = nx.DiGraph()

    def maybe_add_nodes(self, *nodes):
        G = self.G
        for node in nodes:
            if node['ident'] not in G.node:
                G.add_node(node['ident'], **node)

    def generic_visit(self, node):
        parent = getattr(node, 'parent', None)
        if parent is None:
            return
        self.maybe_add_nodes(node, parent)
        parent_id = parent['ident']
        node_id = node['ident']
        self.G.add_edge(parent_id, node_id)

    def finalize(self):
        return self.G


class DiGraphLoader(object):

    def __init__(self, G):
        self.G = G
        root_id = '/us/usc'
        self.root = Node(G.node[root_id])
        self.seen = {root_id: self.root}

    def build(self):
        for node in self.G.nodes():
            self.add_node(node)
        for edge in self.G.edges():
            self.add_edge(*edge)
        return self.root

    def add_node(self, node_id):
        if node_id in self.seen:
            return
        node = self.G.node[node_id]
        node = Node(**node)
        self.seen[node_id] = node

    def add_edge(self, src, dest):
        src = self.seen[src]
        dest = self.seen[dest]
        src.append(dest)


class Node(Node):

    def to_digraph(self):
        root = self.getroot()
        return DiGraphRenderer().visit(root)

    @classmethod
    def from_digraph(cls, G):
        return DiGraphLoader(G).build()

    def citation(self):
        if self['tag'] == 'title':
            return u'{title[num]} U.S.C.'.format(self=self, **self.ctx)
        elif self['tag'] == 'section':
            return u'{title[num]} U.S.C. \xa7 {self[num]}'.format(self=self, **self.ctx)
        elif 'section' in self.ctx:
            citation = self.ctx['section'].citation()
            enums = []
            this = self
            while not this.get('structure'):
                if 'num' in this:
                    enums.append(u'(%s)' % this['num'])
                this = this.parent
            return '%s%s' % (citation, ''.join(enums[::-1]))

    def draw(self):
        G = self.getroot().to_digraph()
        pos = nx.graphviz_layout(G)

        labels = {}
        for node in G.nodes():
            last = node.split('/').pop()
            labels[node] = last

        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos, labels, font_size=10)


class CitationMetadataVisitor(Visitor):

    def generic_visit(self, node):
        if 'tag' in node:
            node.ctx[node['tag']] = node


def fromdata(data):
    '''This is the top-level function for running intermediate
    steps for hydrating api responses. For example, running the visitor
    annotates the data with the necessary info to display basic citations.
    '''
    tree = Node.fromdata(data['response'])
    CitationMetadataVisitor().visit(tree)
    return tree