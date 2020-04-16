from pyshacl import validate
from rdflib import Graph
import inspectVocabs
import os
import sys

# returns triple with (coforms : bool, result_graph : rdflib.Graph, result_text: string)
def validateOntologyGraph(ontograph, shaclgraph):
    r = validate(ontograph, shacl_graph=shaclgraph, ont_graph=None, inference='none', abort_on_error=False, meta_shacl=False, debug=False)
    return r


def loadShaclGraph():
    shaclgraph = Graph()
    shaclgraph.parse(os.path.abspath(os.path.dirname(sys.argv[0])) + os.sep + "onto_shacl.ttl")
    return shaclgraph



def printGraphToTurtleFile(graph, filepath):    
    with open(filepath, "w+") as turtlefile:
        print(graph.serialize(format='turtle'), file=turtlefile)