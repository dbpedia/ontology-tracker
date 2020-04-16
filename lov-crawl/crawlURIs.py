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
import ontoFiles

# url to get all vocabs and their resource
lovOntologiesURL="https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/list"

urlRegex=r"https?://(.+?)/(.*)"

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



def getLastModifiedFromResponse(response):
  if "last-modified" in response.headers.keys():
    return response.headers["last-modified"]
  else:
    return ""

def getFileEnding(response, accHeader):
  if "Content-Type" in response.headers.keys():
    contentType = response.headers["content-type"]
    contentType = contentType.split("/")[1]
    if contentType == "octet-stream":
      contentType = accHeader
    if contentType == "html":
      return ".html"
    elif contentType == "rdf+xml":
      return ".owl"
    elif contentType == "ntriples":
      return ".nt"
    elif contentType == "turtle":
      return ".ttl"
    else:
      return ""
  else:
    return ""

def downloadSource(uri, path, name, accHeader):
    lastModified=""
    try:
        acc_header = {'Accept': accHeader}
        response=requests.get(uri, headers=acc_header, timeout=30, allow_redirects=True)
        lastModified=getLastModifiedFromResponse(response)
        print("Status: " + str(response.status_code))
        if response.status_code < 400:
          with open(path + os.sep + name + ".owl", "w+") as ontfile:
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

def crawlLOV(dataPath, version):
    req = requests.get(lovOntologiesURL)
    json_data=req.json()
    failed_ontologies="dead-ontologies"
    for dataObject in json_data:
      
        vocab_uri=dataObject["uri"]
        groupId, artifact = generateGroupAndArtifactFromUri(vocab_uri)
        
        versionPath=dataPath + os.sep + groupId + os.sep + artifact
        filePath=versionPath + os.sep + version
        os.makedirs(filePath, exist_ok=True)
        
        print("Processing: VocabURI: " + vocab_uri)

        downloadSucessful, lastMod=downloadSource(vocab_uri, filePath, artifact, "application/rdf+xml")
        if downloadSucessful:
          rapperLog=ontoFiles.parseRDFSource(filePath + os.sep + artifact + ".owl", filePath, artifact, outputType="turtle")
          ontoFiles.parseRDFSource(filePath + os.sep + artifact + ".owl", filePath, artifact, outputType="ntriples")
          ontoFiles.writeVocabInformation(vocab_uri, lastMod, rapperLog, filePath, artifact)
        else:
          filePath= failed_ontologies + os.sep + artifact + version
          os.makedirs(filePath)
          ontoFiles.writeVocabInformation(vocab_uri, "", "", "", artifact)
