import ontoFiles
import subprocess
from rdflib import compare
import inspectVocabs
import stringTools
import requests

def runComm(oldFile, newFile):
    process = subprocess.Popen(["LC_ALL=C","comm", "-3", oldFile, newFile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stout, stderr = process.communicate()

def sortFile(sourcePath, targetpath):
    with open(targetpath, "w+") as targetfile:
        process = subprocess.Popen(["LC_ALL=C", "sort", "-u"], stdout=targetfile, stderr=subprocess.PIPE)
        stderr = process.communicate()[1]

def graphDiff(oldGraph, newGraph):
    oldIsoGraph = compare.to_isomorphic(oldGraph)
    newIsoGraph = compare.to_isomorphic(newGraph)
    return compare.graph_diff(oldIsoGraph, newIsoGraph)

def checkForNewVersion(vocab_uri, oldETag, oldLastMod, bestHeader):
  # when both of the old values are not compareable, always download and check
  if stringTools.isNoneOrEmpty(oldETag) and stringTools.isNoneOrEmpty(oldLastMod):
    return True
  acc_header = {'Accept': bestHeader}
  try:
    response = requests.head(vocab_uri, headers=acc_header, timeout=30, allow_redirects=True)
    if response.status_code < 400:
      newETag = stringTools.getEtagFromResponse(response)
      newLastMod = stringTools.getLastModifiedFromResponse(response)
      if not stringTools.isNoneOrEmpty(newETag) and not stringTools.isNoneOrEmpty(oldETag):
        if oldETag != newETag:
          return True
        else:
          return False
      elif not stringTools.isNoneOrEmpty(oldLastMod) and not stringTools.isNoneOrEmpty(newLastMod):
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