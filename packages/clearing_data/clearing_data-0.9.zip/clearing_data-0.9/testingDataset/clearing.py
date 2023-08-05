from core.file.utils import *
import Image

def folderCheck(path):
    """ function(string)->boolean,list,list
    Checks if a folder hs 3 subflders named 'video' 'Tele' 'Wide'

    arguments:path
    returns boolean,subflders list,expected folder list
    """
    folders = [i for i in os.listdir(path)]
    sortedfolders = sorted(folders)

    return [sortedfolders == ['Tele', 'Wide','video'], sortedfolders , ['Tele', 'Wide','video']]


def extentionCheck(path):
    """ function(string)->list
    Checks if a folder's that subfolders contains only '.jpg' files

    arguments:path
    returns list of all non '.jpg' files
    """
    failExtentions =[]
    folders =[fol for fol in [os.path.join(path,i) for i in os.listdir(path) if i != 'video']]
    for j in folders:
        [failExtentions.append(i) for i in os.listdir(j) if '.jpg' !=os.path.splitext(i)[1]]

    return failExtentions

def checkImage(path):
    """ function(string)->list
    Checks if a folder's that subfolders contains only valid Image files

    arguments:path
    returns list of all non valid Image files
    """
    size = (128, 128)
    failImages = []

    for img in os.listdir(path):
        if os.path.splitext(img)[1] != '.db':
            try:
                myimg = Image.open(os.path.join(path,img))
                newimg = myimg.resize(size,Image.ANTIALIAS)
            except IOError:
                failImages.append(img)
                print "lathos image"

    return failImages

def deleteNonJpg(path):
    for i in os.listdir(path):
        if os.path.splitext(i)[1] != '.jpg':
            os.remove(i)





