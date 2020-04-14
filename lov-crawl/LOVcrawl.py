import requests
import subprocess
import re
import os
import sys
from datetime import datetime
from dateutil.parser import parse as parsedate
import rdflib
from rdflib import OWL
from rdflib import RDFS
from rdflib.namespace import DCTERMS
import json

# url to get all vocabs and their resource
datasetUrl="https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/list"

urlRegex=r"https?://(.+?)/(.*)"

rapperRegex=re.compile(r"^rapper: (?:Error|Warning).*$")

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

def returnRapperErrors(rapperLog):
  matches = []
  for line in rapperLog.split("\n"):
    if rapperRegex.match(line):
      matches.append(line)
      
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

def writeVocabInformation(definedByUri, lastModified, rapperErrors, pathToFile, filename):
  vocabInformation={}
  vocabInformation["ontology-resource"] = definedByUri
  vocabInformation["lastModified"] = lastModified
  vocabInformation["rapperErrorLog"] = rapperErrors
  with open(pathToFile + os.sep + filename + ".json", "w+") as outfile:
    json.dump(vocabInformation, outfile, indent=4, sort_keys=True)

def getLastModifiedFromResponse(response):
  if "last-modified" in response.headers.keys():
    return response.headers["last-modified"]
  else:
    return ""

def downloadSource(uri, path, name):
    lastModified=""
    try:
        acc_header = {'Accept': 'application/rdf+xml'}
        with open(path + os.sep + name + ".owl", "w+") as ontfile:
            response=requests.get(uri, headers=acc_header, timeout=30, allow_redirects=True)
            lastModified=getLastModifiedFromResponse(response)
            print("Status: " + str(response.status_code))
            if response.status_code < 400:
                print(response.text, file=ontfile)
                return True, lastModified
            else:
                return False, lastModified
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects, cancel parsing...")
        return False, lastModified
    except TimeoutError:
        print("Timed out during parsing: "+uri)
        return False, lastModified
    except requests.exceptions.ConnectionError:
        print("Bad Connection "+ uri)
        return False, lastModified
    except requests.exceptions.ReadTimeout:
        print("Connection timed out for URI ", uri)
        return False, lastModified

def rapperTheSource(uri, path, name):
  try:
    acc_header = {'Accept': 'application/rdf+xml'}
    header=requests.head(uri, headers=acc_header, timeout=30, allow_redirects=True)
    print("File response: "+str(header.status_code))
    if header.status_code < 400:
      lastModifiedDate=getLastModifiedFromResponse(header)
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

def generateTurtleFromVocabfile(vocabfile, targetpath, name):
  print("Parsing the vocabulary as N-Triples...")
  with open(targetpath + os.sep + name + ".ttl", "w+") as ontfile:
    process = subprocess.Popen(["rapper", "-g", vocabfile, "-o", "turtle"], stdout=ontfile, stderr=subprocess.PIPE)
    stderr=process.communicate()[1].decode("utf-8")
    print(stderr)
    return returnRapperErrors(stderr)

def generateNtriplesFromVocabfile(vocabfile, targetpath, name):
  print("Parsing the vocabulary as N-Triples...")
  with open(targetpath + os.sep + name + ".nt", "w+") as ontfile:
    process = subprocess.Popen(["rapper", "-i", "turtle", vocabfile, "-o", "ntriples"], stdout=ontfile, stderr=subprocess.PIPE)
    stderr=process.communicate()[1]
    print(stderr.decode("utf-8"))

def crawlLOV(dataPath, version):
    req = requests.get(datasetUrl)
    json_data=req.json()
    for dataObject in json_data:
      
        vocab_uri=dataObject["uri"]
        groupId, artifact = generateGroupAndArtifactFromUri(vocab_uri)
        
        versionPath=dataPath + os.sep + groupId + os.sep + artifact
        filePath=versionPath + os.sep + version
        os.makedirs(filePath, exist_ok=True)
        
        print("Processing: VocabURI: " + vocab_uri)

        if not os.path.isfile(filePath + os.sep + artifact + ".ttl"):
            downloadSucessful, lastMod=downloadSource(vocab_uri, filePath, artifact)
            if downloadSucessful:
              rapperLog=generateTurtleFromVocabfile(filePath + os.sep + artifact + ".owl", filePath, artifact)
              generateNtriplesFromVocabfile(filePath + os.sep + artifact + ".ttl", filePath, artifact)
              writeVocabInformation(vocab_uri, lastMod, rapperLog, filePath, artifact)
            else:
              if os.path.isfile(filePath + os.sep + artifact + ".owl"):
                os.remove(filePath + os.sep + artifact + ".owl")
              os.rmdir(filePath)
        else:
            print("Already loaded: " + filePath + os.sep + artifact + ".owl")
