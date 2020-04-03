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

rapperRegex=r"^rapper: (?:Error|Warning).*"

def getGraphOfVocabFile(filepath, rdfFormat):
  graph = rdflib.Graph()
  graph.parse(filepath, format=rdfFormat)
  return graph

def returnRapperErrors(rapperLog):
  matches=re.findall(rapperRegex, rapperLog)
  if matches is []:
    return ""
  else:
    return ";".join(matches)

def generateGroupAndArtifactFromUri(vocab_uri):
  matcher=re.search(urlRegex, vocab_uri)
  groupId=matcher.group(1)
  artifact=matcher.group(2)
  if artifact != "":
    if artifact[-1] == "#" or artifact[-1] == "/":
      artifact=artifact[:-1]
    artifact=artifact.replace("/", "--").replace("_", "--").replace(".", "--")
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
  return results

# returns the non information resource of an ontology, representing the entity of the ontology
def getDefinedByUris(ontgraph):
  result=ontgraph.query(
        """
        SELECT DISTINCT ?defbyUri
        WHERE {
            ?s rdfs:isDefinedBy ?defbyUri .
        }
        """ )
  return results

def writeVocabInformation(definedByUri, lastModified, rapperErrors, pathToFile):
  vocabInformation={}
  vocabInformation["definedByURI"] = definedByUri
  vocabInformation["lastModified"] = lastModified
  vocabInformation["rapperErrorLog"] = rapperErrors
  with open(pathToFile + os.sep + "vocabInformation.json", "w+") as outfile:
    json.dump(vocabInformation, outfile, indent=4, sort_keys=True)

def getLastModified(url):
  try:
    acc_header = {'content-type': 'application/rdf+xml'}
    r=requests.head(url, headers=acc_header, timeout=30, allow_redirects=True)
    if "last-modified" in r.headers.keys():
      url_time = r.headers['last-modified']
    else:
      url_time = "blabla"
    return url_time
  except requests.exceptions.TooManyRedirects:
    print("Too many redirects, cancel parsing...")
  except TimeoutError:
    print("Timed out during parsing: "+url)
  except requests.exceptions.ConnectionError:
    print("Bad Connection "+ url)
  except requests.exceptions.ReadTimeout:
    print("Connection timed out for URI ", url)

def getLastModifiedFromHeader(header):
  if "last-modified" in header.headers.keys():
    return header.headers["last-modified"]
  else:
    return ""

def downloadSource(uri, path, name):
    try:
        acc_header = {'content-type': 'application/rdf+xml'}
        with open(path + "/" + name + ".rdf", "w+") as ontfile:
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
      with open(path + "/" + name + ".ttl", "w+") as ontfile:
        process = subprocess.Popen(["rapper", "-i", "rdfxml", uri, "-o", "turtle"], stdout=ontfile, stderr=subprocess.PIPE)

        none, stderr=process.communicate()
        print(stderr.decode("utf-8"))
        writeVocabInformation(uri, lastModifiedDate, returnRapperErrors(stderr.decode("utf-8")), path)
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
  with open(targetpath + "/" + name + ".nt", "w+") as ontfile:
    process = subprocess.Popen(["rapper", "-i", "turtle", vocabfile, "-o", "ntriples"], stdout=ontfile, stderr=subprocess.PIPE)
    none, stderr=process.communicate()
    print(stderr.decode("utf-8"))

def makeTheDirs(path):
  # i dont know why os.makedirs was not working
  dirs=path.split("/")
    
  for directory in dirs:
    if dirs.index(directory) == 0:
      fullpath=directory
    else:
      fullpath="/".join(dirs[0:dirs.index(directory)]) + "/" + directory
    if not os.path.isdir(fullpath):
      os.mkdir(fullpath)

def crawl_lov(dataPath):
    req = requests.get(datasetUrl)
    json_data=req.json()
    version=datetime.now().strftime("%Y.%m.%d-%H%M%S")
    for dataObject in json_data:
        vocab_uri=dataObject["uri"]
        print("Processing: VocabURI: " + vocab_uri)
        groupId, artifact = generateGroupAndArtifactFromUri(vocab_uri)
        filePath=dataPath + "/" + groupId + "/" + artifact + "/" + version
        makeTheDirs(filePath)
        if not os.path.isfile(filePath + "/" + artifact + ".ttl"):
            rapperedSucessfull=rapperTheSource(vocab_uri, filePath, artifact)
            if rapperedSucessfull:
              getNtriplesFromVocabfile(filePath + "/" + artifact + ".ttl", filePath, artifact)
        else:
            print("Already loaded: " + filePath + "/" + artifact + ".ttl")

crawl_lov(sys.argv[1])
