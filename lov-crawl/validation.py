from pyshacl import validate
from rdflib import Graph
import inspectVocabs
import os
import sys

def loadShaclGraph():
    shaclgraph = Graph()
    shaclgraph.parse(os.path.abspath(os.path.dirname(sys.argv[0])) + os.sep + "onto_shacl.ttl", format="turtle")
    return shaclgraph

shaclGraph = loadShaclGraph()

# returns triple with (conforms : bool, result_graph : rdflib.Graph, result_text: string)
def validateOntologyGraph(ontograph):
    r = validate(ontograph, shacl_graph=shaclGraph, ont_graph=None, inference='none', abort_on_error=False, meta_shacl=False, debug=False)
    return r


def printGraphToTurtleFile(graph, filepath):    
    graph.serialize(format='turtle', destination=filepath)