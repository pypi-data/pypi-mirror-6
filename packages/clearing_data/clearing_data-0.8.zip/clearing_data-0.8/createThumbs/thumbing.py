
from MediaHandler.Agents import *

def runThumpnailing():
    sourcePath = raw_input("give me path of the source folder:")
    targetPath = raw_input("give me path of the target folder:")
    try:
       QualityDrop(sourcePath,targetPath)
       print "all good check for target path folder"
    except IOError:
       print "Something went wrong"

if  __name__ == "__main__":
    runThumpnailing()
