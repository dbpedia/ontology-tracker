from pyshacl import validate
import pprint
from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDFS, RDF, DCTERMS, OWL
import inspectVocabs

# returns triple with (coforms : bool, result_graph : rdflib.Graph, result_text: string)
def validateOntologyGraph(ontograph, shaclgraph):
    r = validate(ontograph, shacl_graph=shaclgraph, ont_graph=None, inference='none', abort_on_error=False, meta_shacl=False, debug=False)
    return r


def generatingShaclForUri(uri):
    shaclgraph = Graph()
    uriref = URIRef(uri)
    sh = Namespace("http://www.w3.org/ns/shacl#")

    anode = BNode()

    shaclgraph.add((uriref, RDF.type, sh.NodeShape))
    # Uri needs to be an ontology
    shaclgraph.add((uriref, sh.targetClass, OWL.Ontology))

    # Adds requiried properties with a anonymous node as reference
    shaclgraph.add((uriref, sh.property, anode))

    # needs to have a min one license which needs to be an uriref
    shaclgraph.add((anode, sh.path, DCTERMS.license))
    shaclgraph.add((anode, sh.minCount, Literal(1)))
    shaclgraph.add((anode, sh.nodeKind, sh.IRI))

    return shaclgraph



def printGraphToTurtleFile(graph, filepath):    
    with open(filepath, "w+") as turtlefile:
        print(graph.serialize(format='turtle'), file=turtlefile)

