# visualize.py - generate graphviz dot source of feature lattice

import graphviz

__all__ = ['featuresystem', 'render_all']

DIRECTORY = 'graphs'

MAXIMAL_LABEL = False
TOPDOWN = False


name_getters = [lambda f: 'f%d' % f.index, lambda f: repr(f)]

label_getters = [
    lambda f: f.string.replace('-', '&minus;'),
    lambda f: f. string_maximal.replace('-', '&minus;')
]

neighbors_getters = [lambda f: f.lower_neighbors, lambda f: f.upper_neighbors]


def featuresystem(fs, highlight, maximal_label, topdown, filename, directory, render, view):
    if maximal_label is None:
        maximal_label = MAXIMAL_LABEL

    if topdown is None:
        topdown = TOPDOWN

    if filename is None:
        filename = 'fs-%s%s.gv' % (fs.key, '-max' if maximal_label else '')

    dot = graphviz.Digraph(
        name=fs.key,
        comment=repr(fs),
        filename=filename,
        directory=directory,
        graph_attr=dict(margin='0'),
        edge_attr=dict(arrowtail='none', penwidth='.5')
    )

    if highlight is not None:
        def node_format(f, dw=set(highlight.downset), up=set(highlight.upset)):
            if f in dw:
                return (('style', 'filled'), ('color', 'gray60'))
            elif f in up:
                return (('style', 'filled'), ('color', 'gray80'))
            elif f is highlight:
                return (('style', 'filled'), ('color', 'gray20'))
    else:
        node_format = lambda f: None


    node_name = name_getters[0]

    node_label = label_getters[bool(maximal_label)]

    node_neighbors = neighbors_getters[bool(topdown)]

    if not topdown:
        dot.edge_attr.update(dir='back')

    sortkey = lambda f: f.index

    for f in fs._featuresets:
        name = node_name(f)
        dot.node(name, node_label(f), node_format(f))
        dot.edges((name, node_name(n))
            for n in sorted(node_neighbors(f), key=sortkey))

    if render or view:
        dot.render(view=view)
    return dot


def render_all(maximal_label=MAXIMAL_LABEL, topdown=TOPDOWN, directory=DIRECTORY):
    from systems import FeatureSystem

    for fs in FeatureSystem:
        featuresystem(fs, None, maximal_label, topdown, None, directory, True, False)
