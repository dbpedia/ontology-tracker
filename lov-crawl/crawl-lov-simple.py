import requests
import subprocess
import re
import os
import sys
from datetime import datetime
from dateutil.parser import parse as parsedate
import rdflib
import json

# url to get all vocabs and their resource
datasetUrl="https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/list"

urlRegex=r"https?://(.+?)/(.*)"

rapperRegex=re.compile(r"^rapper: (?:Error|Warning).*$")


def getLabelFromJsonObject(jsonObj):
  if "titles" in jsonObj.keys() and "value" in jsonObj["titles"][0]:
    return jsonObj["titles"][0]["value"]
  else:
    return ""

def writeMarkdownDescription(path, artifact, label, explaination, description=""):

  with open(path  + os.sep + artifact + ".md", "w+") as mdfile:
    mdstring=(f"# {label}\n"
            f"{explaination}\n"
            "\n"
            f"{description}")
    print(mdstring, file=mdfile)

#removes recursively all dirs that are empty or just contain empty files or directories
def deleteEmptyDirsRecursive(startpath):
  if os.path.isdir(startpath):
    for pathname in os.listdir(startpath):
      if os.path.isdir(startpath + os.sep + pathname):
        deleteEmptyDirsRecursive(startpath + os.sep + pathname)
      elif os.path.isfile(startpath + os.sep + pathname):
        if os.stat(startpath + os.sep + pathname).st_size == 0:
          os.remove(startpath + os.sep + pathname)
    if len(os.listdir(startpath)) == 0:
      os.rmdir(startpath)
  else:
    print(f"Not a directory: {startpath}")

def getGraphOfVocabFile(filepath, rdfFormat):
  graph = rdflib.Graph()
  graph.parse(filepath, format=rdfFormat)
  return graph

def returnRapperErrors(rapperLog):
  matches = []
  for line in rapperLog.split("\n"):
    if rapperRegex.match(line):
      matches.append(line)
      
  print("Rapper Error Matches:")
  print(matches)
  if matches is []:
    return ""
  else:
    return ";".join(matches)

def generateGroupAndArtifactFromUri(vocab_uri):
  matcher=re.search(urlRegex, vocab_uri)
  groupId=matcher.group(1)
  artifact=matcher.group(2)
  if artifact != "":
    if artifact[-1] == "#" or artifact[-1] == os.sep:
      artifact=artifact[:-1]
    artifact=artifact.replace(os.sep, "--").replace("_", "--").replace(".", "--")
  else:
    artifact="vocabulary"
  return groupId, artifact

# returns the non information resource of an ontology, representing the entity of the ontology
def getNIRofOntology(ontgraph):
  result=ontgraph.query(
        """
        SELECT DISTINCT ?nir
        WHERE {
            ?nir <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .
        }
        """ )
  return result

# returns the non information resource of an ontology, representing the entity of the ontology
def getDefinedByUris(ontgraph):
  result=ontgraph.query(
        """
        SELECT DISTINCT ?defbyUri
        WHERE {
            ?s rdfs:isDefinedBy ?defbyUri .
        }
        """ )
  return result

def writeVocabInformation(definedByUri, lastModified, rapperErrors, pathToFile, filename):
  vocabInformation={}
  vocabInformation["ontology-resource"] = definedByUri
  vocabInformation["lastModified"] = lastModified
  vocabInformation["rapperErrorLog"] = rapperErrors
  with open(pathToFile + os.sep + filename + ".json", "w+") as outfile:
    json.dump(vocabInformation, outfile, indent=4, sort_keys=True)

def getLastModifiedFromHeader(header):
  if "last-modified" in header.headers.keys():
    return header.headers["last-modified"]
  else:
    return ""

def downloadSource(uri, path, name):
    try:
        acc_header = {'content-type': 'application/rdf+xml'}
        with open(path + os.sep + name + ".rdf", "w+") as ontfile:
            response=requests.get(uri, headers=acc_header, timeout=30, allow_redirects=True)
            print("Status: " + str(response.status_code))
            if response.status_code < 400:
                print(response.text, file=ontfile)
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects, cancel parsing...")
    except TimeoutError:
        print("Timed out during parsing: "+uri)
    except requests.exceptions.ConnectionError:
        print("Bad Connection "+ uri)
    except requests.exceptions.ReadTimeout:
        print("Connection timed out for URI ", uri)

def rapperTheSource(uri, path, name):
  try:
    acc_header = {'Accept': 'application/rdf+xml'}
    header=requests.head(uri, headers=acc_header, timeout=30, allow_redirects=True)
    print("File response: "+str(header.status_code))
    if header.status_code < 400:
      lastModifiedDate=getLastModifiedFromHeader(header)
      with open(path + os.sep + name + ".ttl", "w+") as ontfile:
        process = subprocess.Popen(["rapper", "-i", "rdfxml", uri, "-o", "turtle"], stdout=ontfile, stderr=subprocess.PIPE)

        stderr=process.communicate()[1]
        print(stderr.decode("utf-8"))
        writeVocabInformation(uri, lastModifiedDate, returnRapperErrors(stderr.decode("utf-8")), path, name)
        return True
    else:
      return False
  except requests.exceptions.TooManyRedirects:
    print("Too many redirects, cancel parsing...")
    return False
  except requests.exceptions.ConnectionError:
    print("Bad Connection "+ uri)
    return False
  except TimeoutError:
    print("Timed out during parsing: "+uri)
    return False
  except requests.exceptions.ReadTimeout:
    print("Connection timed out for URI ", uri)
    return False

def getNtriplesFromVocabfile(vocabfile, targetpath, name):
  print("Parsing the vocabulary as N-Triples...")
  with open(targetpath + os.sep + name + ".nt", "w+") as ontfile:
    process = subprocess.Popen(["rapper", "-i", "turtle", vocabfile, "-o", "ntriples"], stdout=ontfile, stderr=subprocess.PIPE)
    stderr=process.communicate()[1]
    print(stderr.decode("utf-8"))

def crawl_lov(dataPath):
    req = requests.get(datasetUrl)
    json_data=req.json()
    version=datetime.now().strftime("%Y.%m.%d-%H%M%S")
    for dataObject in json_data:
      
        vocab_uri=dataObject["uri"]
        groupId, artifact = generateGroupAndArtifactFromUri(vocab_uri)
        
        versionPath=dataPath + os.sep + groupId + os.sep + artifact
        filePath=versionPath + os.sep + version
        os.makedirs(filePath, exist_ok=True)
        
        print("Processing: VocabURI: " + vocab_uri)

        vocab_label=getLabelFromJsonObject(dataObject)
        print("Label: " + vocab_label)
        if vocab_label == "":
          vocab_label= artifact + " vocabulary"
        vocab_description=f"This ontology was automatically crawled from https://lov.linkeddata.es to be deployed to the dbpedia databus"
        if not os.path.isfile(filePath + os.sep + artifact + ".ttl"):
            rapperedSucessfull=rapperTheSource(vocab_uri, filePath, artifact)
            if rapperedSucessfull:
              getNtriplesFromVocabfile(filePath + os.sep + artifact + ".ttl", filePath, artifact)
              writeMarkdownDescription(versionPath, artifact, vocab_label, vocab_description)
            else:
              if os.path.isfile(filePath + os.sep + artifact + ".ttl"):
                os.remove(filePath + os.sep + artifact + ".ttl")
              os.rmdir(filePath)
        else:
            print("Already loaded: " + filePath + os.sep + artifact + ".ttl")

rootdir=sys.argv[1]

crawl_lov(rootdir)
deleteEmptyDirsRecursive(rootdir)