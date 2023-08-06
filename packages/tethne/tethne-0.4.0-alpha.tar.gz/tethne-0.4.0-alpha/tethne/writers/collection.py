"""
Write :class:`.GraphCollection` to a structured data format.

.. autosummary::

   to_dxgmml
   
"""

import networkx as nx
import pickle as pk

def to_dxgmml(C, path): # [#61510094]
    """
    Writes a :class:`.GraphCollection` to 
    `dynamic XGMML. <https://code.google.com/p/dynnetwork/wiki/DynamicXGMML>`_.
    
    Dynamic XGMML is a schema for describing dynamic networks in Cytoscape 3.0.
    This method assumes that `Graph` indices are orderable points in time 
    (e.g. years). The "start" and "end" of each node and edge are determined by 
    periods of consecutive appearance in the :class:`.GraphCollection` . Node 
    and edge attributes are defined for each `Graph`. in the 
    :class:`.GraphCollection`.
    
    For example, to build and visualize an evolving co-citation network:
    
    .. code-block:: python

       >>> # Load some data.
       >>> import tethne.readers as rd
       >>> papers = rd.wos.read(datapath)

       >>> # Build a DataCollection, and slice it temporally using a
       >>> #  4-year sliding time-window.
       >>> from tethne.data import DataCollection, GraphCollection
       >>> D = DataCollection(papers)
       >>> D.slice('date', 'time_window', window_size=4)

       >>> # Generate a GraphCollection of co-citation graphs.
       >>> from tethne.builders import paperCollectionBuilder
       >>> builder = paperCollectionBuilder(D)
       >>> C = builder.build('date', 'cocitation', threshold=2)

       >>> # Write the GraphCollection as a dynamic network.
       >>> import tethne.writers as wr
       >>> wr.collection.to_dxgmml(C, "/path/to/network.xgmml")
    
    Parameters
    ----------
    C : :class:`.GraphCollection`
        The :class:`.GraphCollection` to be written to XGMML.
    path : str
        Path to file to be written. Will be created/overwritten.

    Notes
    -----
    Period start and end dates in this method are inclusive, whereas XGMML end
    dates are exclusive. Hence +1 is added to all end dates when writing XGMML.
    """

    nodes = {}
    for n in C.nodes():
        nodes[n] = { 'periods' : [] }   # Each period will be a dict with
                                        #  'start' and 'end' values.
    edges = {}
    for e in C.edges():
        edges[e] = { 'periods' : [] }

    # Build node list.
    current = []
    for k in sorted(C.graphs.keys()):
        G = _strip_list_attributes(C[k])
        preceding = current
        current = []
        for n in G.nodes(data=True):
            if n[0] not in preceding:   # Looking for gaps in presence of node.
                nodes[n[0]]['periods'].append( { 'start': k, 'end': k } )
            else:
                if k > nodes[n[0]]['periods'][-1]['end']:
                    nodes[n[0]]['periods'][-1]['end'] = k
            current.append(n[0])

            nodes[n[0]][k] = {}
            for attr, value in n[1].iteritems():
                if type(value) is str:
                    value = value.replace("&", "&amp;").replace('"', '')
                nodes[n[0]][k][attr] = value

    # Build edge list.
    current = []
    for k in sorted(C.graphs.keys()):
        G = _strip_list_attributes(C[k])
        preceding = current
        current = []
        for e in G.edges(data=True):
            e_key = (e[0], e[1])
            if e_key not in preceding:   # Looking for gaps in presence of edge.
                edges[e_key]['periods'].append( { 'start': k, 'end': k } )
            else:
                if k > edges[e_key]['periods'][-1]['end']:
                    edges[e_key]['periods'][-1]['end'] = k
            current.append(e_key)

            edges[e_key][k] = {}
            for attr, value in e[2].iteritems():
                if type(value) is str:
                    value = value.replace("&", "&amp;").replace('"', '')
                edges[e_key][k][attr] = value

    # Write graph to XGMML.
    nst = '\t<node label="{0}" id="{0}" start="{1}" end="{2}">\n'
    ast = '\t\t<att name="{0}" type="{1}" value="{2}" start="{3}" end="{4}"/>\n'
    
    with open(path, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write('<graph>\n')
        for n in nodes.keys():
            for period in nodes[n]['periods']:
                label = str(n).replace("&", "&amp;").replace('"', '')
                
                f.write(nst.format(label, period['start'], period['end']+1))

                for i in sorted(nodes[n].keys()):
                    if period['start'] <= i <= period['end']:
                        for attr, value in nodes[n][i].iteritems():
                            # Type names are slightly different in XGMML.
                            if type(value) is str: dtype = 'string'
                            if type(value) is int: dtype = 'integer'
                            if type(value) is float: dtype = 'real'
                            attr = str(attr).replace("&", "&amp;")
                            f.write(ast.format(attr, dtype, value, i, i+1))
                f.write('\t</node>\n')

        for e in edges.keys():
            for period in edges[e]['periods']:
                src = str(e[0]).replace("&", "&amp;").replace('"', '')
                tgt = str(e[1]).replace("&", "&amp;").replace('"', '')
                start = str(period['start'])
                end = str(period['end']+1)
                f.write('\t<edge source="' + src + '" target="' + tgt \
                            + '" start="'+ start + '" end="' + end + '">\n')

                for i in sorted(edges[e].keys()):
                    if period['start'] <= i <= period['end']:
                        for attr, value in edges[e][i].iteritems():
                            # Type names are slightly different in XGMML.
                            if type(value) is str: dtype = 'string'
                            if type(value) is int: dtype = 'integer'
                            if type(value) is float: dtype = 'real'
                            f.write('\t\t<att name="'+str(attr)+'" type="'\
                                    +dtype+'" value="'+str(value)+'" start="'\
                                    +str(i)+'" end="'\
                                    +str(i+1)+'" />\n'.replace("&", "&amp;"))
                f.write('\t</edge>\n')
        f.write('</graph>')
        
def _strip_list_attributes(G):
    for n in G.nodes(data=True):
        for k,v in n[1].iteritems():
            if type(v) is list:
                G.node[n[0]][k] = str(v)
    for e in G.edges(data=True):
        for k,v in e[2].iteritems():
            if type(v) is list:
                G.edge[e[0]][e[1]][k] = str(v)

    return G        
