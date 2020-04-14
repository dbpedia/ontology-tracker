import os
import sys
import rdflib
from rdflib import OWL
from rdflib import RDFS
from rdflib.namespace import DCTERMS
from rdflib.namespace import DC

def getGraphOfVocabFile(filepath):
  rdfFormat=rdflib.util.guess_format(filepath)
  graph = rdflib.Graph()
  graph.parse(filepath, format=rdfFormat)
  return graph

#Relevant properties:
# rdfs:label
# rdfs:comment
# rdfs:description
# dcterms:license
# dcterms:title
# dcterms:description
# dcterms:abstract
# dc:title
# dc:description

# Returns the relevant rdfs info about a ontology (uri, rdfs:label, rdfs:comment, rdfs:description)
def getRelevantRDFSVocabInfo(graph):
    queryString=(
        "SELECT DISTINCT ?uri ?label ?comment ?description \n"
        "WHERE {\n"
        " ?uri a owl:Ontology .\n"
        " OPTIONAL { ?uri rdfs:label ?label FILTER langMatches(lang(?label), \"en\")}\n"    
        " OPTIONAL { ?uri rdfs:comment ?comment }\n"
        " OPTIONAL { ?uri rdfs:description ?description }\n"
        "} LIMIT 1"
        )
    result=graph.query(queryString, initNs={"owl": OWL, "rdfs":RDFS})
    if result != None and len(result) > 0:
        for row in result:
            return row
    else:
        return (None, None, None, None)

# returns the relevant dcterms values (uri, dcterms:license, dcterms:title, dcterms:abstract, dcterms:description)
def getRelevantDCTERMSVocabInfo(graph):
    queryString=(
        "SELECT DISTINCT ?uri ?license ?title ?abstract ?description \n"
        "WHERE {\n"
        " ?uri a owl:Ontology .\n"
        " OPTIONAL { ?uri dcterms:license ?license }\n"   
        " OPTIONAL { ?uri dcterms:title ?title }\n" 
        " OPTIONAL { ?uri dcterms:abstract ?astract }\n"
        " OPTIONAL { ?uri dcterms:description ?description }\n"
        "} LIMIT 1"
        )
    result=graph.query(queryString, initNs={"owl": OWL, "dcterms": DCTERMS})
    if result != None and len(result) > 0:
        for row in result:
            return row
    else:
        return (None, None, None, None, None)


# returns the relevant dc values (uri, dc:title, dc:description)
def getRelevantDCVocabInfo(graph):
    queryString=(
        "SELECT DISTINCT ?uri ?title ?description\n"
        "WHERE {\n"
        " ?uri a owl:Ontology .\n"
        " OPTIONAL { ?uri dc:title ?license }\n"
        " OPTIONAL { ?uri dc:description ?description }\n"    
        "} LIMIT 1"
        )
    result=graph.query(queryString, initNs={"owl": OWL, "dc": DC})
    if result != None and len(result) > 0:
        for row in result:
            return row
    else:
        return (None, None, None)

# returns the non information resource of an ontology, representing the entity of the ontology
def getDefinedByUris(ontgraph):
    result=ontgraph.query(
        """
        SELECT DISTINCT ?defbyUri
        WHERE {
            ?s rdfs:isDefinedBy ?defbyUri .
        } LIMIT 1
        """ )
    if result != None and len(result) > 0:
        for row in result:
            return row
    else:
        return None


def inspectVocabs(rootdir):
    for group in os.listdir(rootdir):
        if not os.path.isdir(rootdir + os.sep +group):
            continue
        for artifact in os.listdir(rootdir + os.sep + group):
            versionDir=rootdir + os.sep + group + os.sep + artifact
            if not os.path.isdir(versionDir):
                continue
            for version in os.listdir(versionDir):
                if not os.path.isdir(versionDir + os.sep + version):
                   continue
                dataPath=versionDir + os.sep + version
                filepath = dataPath + os.sep + artifact + ".nt"
                if not os.path.isfile(filepath):
                    continue
                print("File: " + filepath)
                #graph = getGraphOfVocabFile(filepath)
                #vocab_uri, vocab_license, vocab_label, vocab_comment, vocab_description = getRelevantVocabInfo(graph)
                #if vocab_uri != None:
                #    print("Uri: ",vocab_uri.n3())
                #if vocab_license != None:
                #    print("License: ",vocab_license.n3())
                #if vocab_label != None:
                #    print("Label: ", vocab_label) 
                #if vocab_comment != None:
                #    print("Comment: ", vocab_comment)
                #if vocab_description != None:
                #    print("Description: ", vocab_description)


            