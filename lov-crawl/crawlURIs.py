import requests
import re
import os
import sys
from datetime import datetime
from dateutil.parser import parse as parsedate
import ontoFiles
import validation
import inspectVocabs
import generatePoms

# docu for failed ontologies
failedGroupDoc = (f"#This group is for all unavailable ontologies\n\n"
                "All the artifacts in this group refer to one vocabulary.\n"
                "The ontologies are part of the Databus Archivo - A Web-Scale Ontology Interface for Time-Based and Semantic Archiving and Developing Good Ontologies.")

# explaination for the md-File
explaination="This ontology is part of the Databus Archivo - A Web-Scale OntologyInterface for Time-Based and SemanticArchiving and Developing Good Ontologies"

# url to get all vocabs and their resource
lovOntologiesURL="https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/list"

# url for the lodo docu service
lodeServiceUrl="https://w3id.org/lode/"

# possible headers for rdf-data
rdfHeaders=["application/rdf+xml", "application/ntriples", "text/turtle", "text/rdf+n3", "application/html"]

urlRegex=r"https?://(.+?)/(.*)"

#should be extended maybe
fileTypeDict = {"turtle": ".ttl", "rdf+xml": ".rdf", "ntriples": ".nt", "rdf+n3":".n3", "html":".html", "xml":".xml"}

# regex to get the content type
contentTypeRegex = re.compile(r"\w+/([\w+-]+)(?:.*)?")

def isNoneOrEmpty(string):
  if string != None and string != "":
    return False
  else:
    return True

def getLodeDocuFile(vocab_uri):
  print("Generating lode-docu...")
  try:
    response = requests.get(lodeServiceUrl + vocab_uri)
    if response.status_code < 400:
      return response.text
    else:
      return None
  except requests.exceptions.TooManyRedirects:
        print("Too many redirects, cancel parsing...")
        return None
  except TimeoutError:
        print("Timed out during parsing: "+vocab_uri)
        return None
  except requests.exceptions.ConnectionError:
        print("Bad Connection "+ vocab_uri)
        return None
  except requests.exceptions.ReadTimeout:
        print("Connection timed out for URI ", vocab_uri)
        return None


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

def determineBestAccHeader(vocab_uri):
  print("Determining the best header for this vocabulary...")
  headerDict = {}
  localTestDir = "./.tmpTestTriples"
  os.makedirs(localTestDir, exist_ok=True)
  for header in rdfHeaders:
    success, filePath = downloadSource(vocab_uri, localTestDir, "testTriples", header)[:2]
    if success:
      tripleNumber = ontoFiles.getParsedTriples(filePath)
      if tripleNumber != None:
        headerDict[header] = tripleNumber
        print("Accept-Header: " + header + "; TripleNumber: " + tripleNumber)
  generatedFiles = [f for f in os.listdir(localTestDir) if os.path.isfile(localTestDir + os.sep + f)]
  for filename in generatedFiles:
    os.remove(os.path.join(localTestDir, filename))
  # return the header with the most triples
  if headerDict == {}:
    return None
  else:
    return [k for k, v in sorted(headerDict.items(), key=lambda item: item[1], reverse=True)][0]


def getLastModifiedFromResponse(response):
  if "last-modified" in response.headers.keys():
    return response.headers["last-modified"]
  else:
    return ""

def getEtagFromResponse(response):
  if "ETag" in response.headers.keys():
    return response.headers["ETag"]
  else:
    return ""
  

def getFileEnding(response, accHeader):
  if "Content-Type" in response.headers.keys():
    contentType = response.headers["content-type"]
    match = contentTypeRegex.search(contentType)
    if match == None:
      return ""
    else:
      contentType = match.group(1)
      if contentType == "octet-stream":
        contentType = accHeader.split("/")[1]
    print("Content Type: " + contentType)
    return fileTypeDict.get(contentType, "")
  else:
    return ""

def downloadSource(uri, path, name, accHeader):
  try:
    acc_header = {'Accept': accHeader}
    response=requests.get(uri, headers=acc_header, timeout=30, allow_redirects=True)
    print("Status: " + str(response.status_code))
    fileEnding = getFileEnding(response, accHeader)
    filePath = path + os.sep + name +"_type=orig"+ fileEnding
    if response.status_code < 400:
      with open(filePath, "w+") as ontfile:
        print(response.text, file=ontfile)
      return True, filePath, response
    else:
      return False, filePath, response
  except requests.exceptions.TooManyRedirects:
    print("Too many redirects, cancel parsing...")
    return False, "", None
  except TimeoutError:
    print("Timed out during parsing: "+uri)
    return False, "", None
  except requests.exceptions.ConnectionError:
    print("Bad Connection "+ uri)
    return False, "", None
  except requests.exceptions.ReadTimeout:
    print("Connection timed out for URI ", uri)
    return False, "", None

def checkForNewVersion(vocab_uri, oldETag, oldLastMod, bestHeader):
  # when both of the old values are not compareable, always download and check
  if isNoneOrEmpty(oldETag) and isNoneOrEmpty(oldLastMod):
    return True
  acc_header = {'Accept': bestHeader}
  try:
    response = requests.head(lodeServiceUrl + vocab_uri, headers=acc_header, timeout=30, allow_redirects=True)
    if response.status_code < 400:
      newETag = getEtagFromResponse(response)
      newLastMod = getLastModifiedFromResponse(response)
      if not isNoneOrEmpty(newETag) and not isNoneOrEmpty(oldETag):
        if oldETag != newETag:
          return True
        else:
          return False
      elif not isNoneOrEmpty(oldLastMod) and not isNoneOrEmpty(newLastMod):
        if oldLastMod != newLastMod:
          return True
        else:
          return False
      else:
        return False
    else:
      return None
  except requests.exceptions.TooManyRedirects:
        print("Too many redirects, cancel parsing...")
        return None
  except TimeoutError:
        print("Timed out: "+vocab_uri)
        return None
  except requests.exceptions.ConnectionError:
        print("Bad Connection "+ vocab_uri)
        return None
  except requests.exceptions.ReadTimeout:
        print("Connection timed out for URI ", vocab_uri)
        return None
  

def generateNewRelease(vocab_uri, filePath, artifact, pathToOrigFile, bestHeader, lastMod, etag, accessDate):
  # generate parsed variants of the ontology
  rapperErrors, rapperWarnings=ontoFiles.parseRDFSource(pathToOrigFile, os.path.join(filePath, artifact+"_type=parsed.ttl"), outputType="turtle", deleteEmpty=True)
  ontoFiles.parseRDFSource(pathToOrigFile, os.path.join(filePath, artifact+"_type=parsed.nt"), outputType="ntriples", deleteEmpty=True)
  triples = ontoFiles.getParsedTriples(pathToOrigFile)
  if triples == None:
    triples = 0
  # shacl-validation
  # uses the turtle file since there were some problems with the blankNodes of rapper and rdflib
  # no empty parsed files since shacl is valid on empty files.
  if os.path.isfile(os.path.join(filePath, artifact+"_type=parsed.ttl")):
    ontoGraph = inspectVocabs.getGraphOfVocabFile(os.path.join(filePath, artifact+"_type=parsed.ttl"))
    conforms, reportGraph, reportText = validation.validateOntologyGraph(ontoGraph)
    print(reportText)
    validation.printGraphToTurtleFile(reportGraph, os.path.join(filePath, artifact+"_type=shaclReport.ttl"))
  else:
    print("No valid syntax, no shacl report")
    conforms = False
    ontoGraph = None
  # write the metadata json file
  ontoFiles.writeVocabInformation(pathToFile=os.path.join(filePath, artifact+"_type=meta.json"),
                                  definedByUri=vocab_uri,
                                  lastModified=lastMod,
                                  rapperErrors=rapperErrors,
                                  rapperWarnings=rapperWarnings,
                                  etag=etag,
                                  tripleSize=triples,
                                  bestHeader=bestHeader,
                                  shaclValidated=conforms,
                                  accessed= accessDate
                                  )
  docustring = getLodeDocuFile(vocab_uri)
  if docustring != None:
    with open(filePath + os.sep + artifact + "_type=generatedDocu.html", "w+") as docufile:
      print(docustring, file=docufile)
  # returns the ontograph for proper metadata generation
  return ontoGraph



# handles a vocab-uri, parameters are 
def handleUri(vocab_uri, index, dataPath):
  groupId, artifact = generateGroupAndArtifactFromUri(vocab_uri)
  version = datetime.now().strftime("%Y.%m.%d-%H%M%S")
  versionPath=dataPath + os.sep + groupId + os.sep + artifact
  filePath=versionPath + os.sep + version
  os.makedirs(filePath, exist_ok=True)
  print("Processing VocabURI: " + vocab_uri)
  i = ontoFiles.checkIfUriInIndex(vocab_uri, index)
  if i == None:
    bestHeader = determineBestAccHeader(vocab_uri)
    isNew = True
  else:
    bestHeader = index[i]["best-header"]
    oldLastMod = index[i]["last-modified"]
    oldETag = index[i]["e-tag"]
    isNew = False

  if not os.path.isfile(os.path.join(dataPath, groupId, "pom.xml")):
    groupDoc=(f"#This group is for all vocabularies hosted on {groupId}\n\n"
            "All the artifacts in this group refer to one vocabulary, deployed in different formats.\n"
            "The ontologies are part of the Databus Archivo - A Web-Scale Ontology Interface for Time-Based and Semantic Archiving and Developing Good Ontologies.")
 
    pomString=generatePoms.generateParentPom(groupId=groupId,
                                            packaging="pom",
                                            modules=[],
                                            packageDirectory=generatePoms.packDir,
                                            downloadUrlPath=generatePoms.downloadUrl,
                                            publisher=generatePoms.pub,
                                            maintainer=generatePoms.pub,
                                            groupdocu=groupDoc,
                                            )
    with open(os.path.join(dataPath, groupId, "pom.xml"), "w+") as parentPomFile:
      print(pomString, file=parentPomFile)


  # check the best header, if its None or the empty string the file is not available
  if bestHeader != None and bestHeader != "":
    downloadSucessful, pathToOrigFile, response=downloadSource(vocab_uri, filePath, artifact, bestHeader)
    accessDate = datetime.now().strftime("%Y.%m.%d; %H:%M:%S")
  else:
    downloadSucessful = False

  if downloadSucessful:
    # get some metadata
    
    lastMod = getLastModifiedFromResponse(response)
    etag = getEtagFromResponse(response)
    # append uri to index with updated values
    if isNew:
      index.append({"vocab-uri":vocab_uri, "last-modified":lastMod, "best-header":bestHeader, "e-tag":etag})
    
    ontograph=generateNewRelease(vocab_uri, filePath, artifact, pathToOrigFile, bestHeader, lastMod, etag, accessDate)
    md_label=artifact + " ontology"
    md_description=""
    license=None
    if ontograph != None:
      labelList = inspectVocabs.getPossibleLabels(ontograph)
      descriptionList = inspectVocabs.getPossibleDescriptions(ontograph)
      if labelList != None:
        possibleLabels = [label for label in labelList if label != None]
      else:
        possibleLabels = []

      if descriptionList != None:
        possibleDescriptions = [desc for desc in descriptionList if desc != None]
      else:
        possibleDescriptions = []
      license =inspectVocabs.getLicense(ontograph)
      if possibleLabels != [] and len(possibleLabels) > 0:
        md_label = possibleLabels[0]
      if possibleDescriptions != [] and len(possibleDescriptions) > 0:
        md_description = possibleDescriptions[0]  
    childpomString = generatePoms.generateChildPom(groupId=groupId,
                                                  version=version,
                                                  artifactId=artifact,
                                                  packaging="jar",
                                                  license=license)
    with open(os.path.join(versionPath, "pom.xml"), "w+") as childPomFile:
      print(childpomString, file=childPomFile)
    generatePoms.writeMarkdownDescription(versionPath, artifact, md_label, explaination, md_description)
  # no need of deploying a new version of unavailable ontologies
  elif not os.path.isfile(os.path.join(versionPath, "pom.xml")):
    # removenot used dirs and files
    ontoFiles.deleteEmptyDirsRecursive(os.path.join(dataPath, groupId))
    if len([dirname for dirname in os.listdir(os.path.join(dataPath, groupId)) if os.path.isdir(os.path.join(dataPath, groupId, dirname))]) == 0:
      os.remove(os.path.join(dataPath, groupId, "pom.xml"))
      os.rmdir(os.path.join(dataPath, groupId))
    # when ontologies are not available, add them to a special group (are the only ones who have an empty string at the key accessed)
    failedPath= os.path.join(dataPath, "unavailable-ontologies", groupId + "--" + artifact, version)
    os.makedirs(failedPath, exist_ok=True)
    # generate parent-pom if not existent
    if not os.path.isfile(os.path.join(dataPath, "unavailable-ontologies", "pom.xml")):
      pomString=generatePoms.generateParentPom(groupId="unavailable-ontologies",
                                            packaging="pom",
                                            modules=[],
                                            packageDirectory=generatePoms.packDir,
                                            downloadUrlPath=generatePoms.downloadUrl,
                                            publisher=generatePoms.pub,
                                            maintainer=generatePoms.pub,
                                            groupdocu=failedGroupDoc,
                                            )

    index.append({"vocab-uri":vocab_uri, "last-modified":"", "best-header":"", "e-tag":""})
    ontoFiles.writeVocabInformation(pathToFile=os.path.join(failedPath, groupId + "--" + artifact + "_type=meta.json"),
                                    definedByUri=vocab_uri,
                                    lastModified="",
                                    rapperErrors="",
                                    rapperWarnings="",
                                    etag="",
                                    tripleSize= 0,
                                    bestHeader="",
                                    shaclValidated=False,
                                    accessed=""
                                    )
    childpomString = generatePoms.generateChildPom(groupId=groupId,
                                                  version=version,
                                                  artifactId=groupId + "--" + artifact,
                                                  packaging="jar",
                                                  license=None)
    generatePoms.writeMarkdownDescription(path=os.path.join(dataPath, "unavailable-ontologies", groupId + "--" + artifact), 
                                          artifact=groupId + "--" + artifact,
                                          label=groupId + "--" + artifact + " ontology", 
                                          explaination=explaination,
                                          description="This is a Ontology wich cant be accessed")
  



def crawlLOV(dataPath):
    req = requests.get(lovOntologiesURL)
    json_data=req.json()
    index = ontoFiles.loadIndexJson()
    for dataObject in json_data:
      vocab_uri=dataObject["uri"]
      handleUri(vocab_uri, index, dataPath)
    ontoFiles.writeIndexJson(index)

        