import os
import sys
import json
import subprocess
import re

rapperErrors=re.compile(r"^rapper: Error.*$")
rapperWarnings=re.compile(r"^rapper: Warning.*$")


def returnRapperErrors(rapperLog):
  errorMatches = []
  warningMatches = []
  for line in rapperLog.split("\n"):
    if rapperErrors.match(line):
      errorMatches.append(line)
    elif rapperWarnings.match(line):
      warningMatches.append(line)
  return ";".join(errorMatches), ";".join(warningMatches)

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

def writeVocabInformation(definedByUri, lastModified, rapperErrors, pathToFile, filename):
  vocabInformation={}
  vocabInformation["ontology-resource"] = definedByUri
  vocabInformation["lastModified"] = lastModified
  vocabInformation["rapperErrorLog"] = rapperErrors
  with open(pathToFile + os.sep + filename + "_type=meta.json", "w+") as outfile:
    json.dump(vocabInformation, outfile, indent=4, sort_keys=True)

def parseRDFSource(sourcefile, targetpath, name, outputType):
  print("Parsing the vocabulary as N-Triples...")
  with open(targetpath + os.sep + name + "_type=parsed.nt", "w+") as ontfile:
    process = subprocess.Popen(["rapper", "-g", sourcefile, "-o", outputType], stdout=ontfile, stderr=subprocess.PIPE)
    stderr=process.communicate()[1].decode("utf-8")
    print(stderr)
    return returnRapperErrors(stderr)