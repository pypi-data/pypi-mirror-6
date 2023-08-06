from __future__ import unicode_literals, print_function
import codecs
import networkx as nx

def make_nx_graph(input_filename):
    """
    Convert a tab-separated "CSV" of concept-to-concept associations to a
    GEXF file, for rendering as a graph.
    """
    G = nx.Graph()
    for line in codecs.open(input_filename, encoding='utf-8'):
        start, end, weight = line.rstrip('\n').split('\t')
        weight = float(weight)
        G.add_edge(start, end, data={'weight': weight})
    return G


