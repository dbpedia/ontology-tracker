import os
import sys
import rdflib
from rdflib import OWL
from rdflib import RDFS
from rdflib.namespace import DCTERMS

def getGraphOfVocabFile(filepath):
  rdfFormat=rdflib.util.guess_format(filepath)
  graph = rdflib.Graph()
  graph.parse(filepath, format=rdfFormat)
  return graph

def getRelevantVocabInfo(graph):
    queryString=(
        "SELECT DISTINCT ?uri ?license ?label ?comment ?description \n"
        "WHERE {\n"
        " ?uri a owl:Ontology .\n"
        " OPTIONAL { ?uri dct:license ?license }\n"
        " OPTIONAL { ?uri rdfs:label ?label }\n"    
        " OPTIONAL { ?uri rdfs:comment ?comment }\n"
        " OPTIONAL { ?uri rdfs:description ?description }\n"
        "} LIMIT 1"
        )
    result=graph.query(queryString, initNs={"owl": OWL, "dct":DCTERMS, "rdfs":RDFS})
    if result != None and len(result) > 0:
        for row in result:
            return row
    else:
        return (None, None, None, None, None)




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
                graph = getGraphOfVocabFile(filepath)
                vocab_uri, vocab_license, vocab_label, vocab_comment, vocab_description = getRelevantVocabInfo(graph)
                if vocab_uri != None:
                    print("Uri: ",vocab_uri.n3())
                if vocab_license != None:
                    print("License: ",vocab_license.n3())
                if vocab_label != None:
                    print("Label: ", vocab_label) 
                if vocab_comment != None:
                    print("Comment: ", vocab_comment)
                if vocab_description != None:
                    print("Description: ", vocab_description)

rootdir=sys.argv[1]

inspectVocabs(rootdir)

            