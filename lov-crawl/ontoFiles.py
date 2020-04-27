import os
import sys
import json
import subprocess
import re
import csv

rapperErrorsRegex=re.compile(r"^rapper: Error.*$")
rapperWarningsRegex=re.compile(r"^rapper: Warning.*$")
rapperTriplesRegex=re.compile(r"rapper: Parsing returned (\d+) triples")


def returnRapperErrors(rapperLog):
  errorMatches = []
  warningMatches = []
  for line in rapperLog.split("\n"):
    if rapperErrorsRegex.match(line):
      errorMatches.append(line)
    elif rapperWarningsRegex.match(line):
      warningMatches.append(line)
  return ";".join(errorMatches), ";".join(warningMatches)

def getTripleNumberFromRapperLog(rapperlog):
  match = rapperTriplesRegex.search(rapperlog)
  if match != None:
    return int(match.group(1))
  else:
    return None

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

def writeVocabInformation(pathToFile, definedByUri, lastModified, rapperErrors, rapperWarnings, etag, tripleSize, bestHeader, shaclValidated, accessed, headerString, nirHeader):
  vocabInformation={}
  vocabInformation["ontology-resource"] = definedByUri
  vocabInformation["accessed"] = accessed
  vocabInformation["lastModified"] = lastModified
  vocabInformation["rapperErrors"] = rapperErrors
  vocabInformation["rapperWarnings"] = rapperWarnings
  vocabInformation["E-Tag"] = etag
  vocabInformation["triples"] = tripleSize
  vocabInformation["best-header"] = bestHeader
  vocabInformation["SHACL-validated"] = shaclValidated
  vocabInformation["resource-header"] = headerString
  vocabInformation["NIR-header"] = nirHeader

  with open(pathToFile, "w+") as outfile:
    json.dump(vocabInformation, outfile, indent=4, sort_keys=True)

def parseRDFSource(sourcefile, filepath, outputType, deleteEmpty=True, silent=False):
  print("Parsing the vocabulary as N-Triples...")
  with open(filepath, "w+") as ontfile:
    process = subprocess.Popen(["rapper", "-g", sourcefile, "-o", outputType], stdout=ontfile, stderr=subprocess.PIPE)
    stderr=process.communicate()[1].decode("utf-8")
    if not silent:
      print(stderr)
  if deleteEmpty:
    returnedTriples = getTripleNumberFromRapperLog(stderr)
    if not silent:
      print("Returned Triples: ", returnedTriples)
    if returnedTriples == None or returnedTriples == 0:
      if not silent:
        print("Parsed file empty, deleting...")
      os.remove(filepath)
  return returnRapperErrors(stderr)

def getParsedTriples(filepath):
  process = subprocess.Popen(["rapper", "-c", "-g", filepath], stderr=subprocess.PIPE)
  try:
    stderr = process.communicate()[1].decode("utf-8")
  except UnicodeDecodeError:
    print("There was a decoding error at parsing " + filepath)
    return None
  return getTripleNumberFromRapperLog(stderr)

# for efficiency the tsv reads in as a dict, with the vocab_uri as the key and (bestHeader, lastMod, etag) as value 
def loadIndex():
  resultDict = {}
  with open(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "vocab_index.tsv"), "r") as indexfile:
    reader = csv.reader(indexfile, delimiter="\t")
    for row in reader:
      print(row)
      vocabUri = row[0]
  return resultDict

def loadIndexJson():
  with open(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "vocab_index.json"), "r") as indexfile:
    jsonIndex = json.load(indexfile)
  return jsonIndex

def loadSimpleIndex():
  with open(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "vocab_index.txt"), "r") as indexfile:
    lines = [line.rstrip() for line in indexfile]
  return lines

def writeSimpleIndex(index):
  with open(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "vocab_index.txt"), "w") as indexfile: 
    print("\n".join(index), file=indexfile)


def writeIndex(index):
  with open(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "vocab_index.tsv"), "w") as indexfile:
    writer = csv.writer(indexfile, delimiter="\t")
    writer.writerows(index)

def checkIfUriInIndex(uri, index):
  for i, uriObj in enumerate(index):
    if uriObj["vocab-uri"] == uri:
      return i
  return None

def writeIndexJson(index):
  with open(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "vocab_index.json"), "w+") as indexfile:
    json.dump(index, indexfile, indent=4, sort_keys=True)