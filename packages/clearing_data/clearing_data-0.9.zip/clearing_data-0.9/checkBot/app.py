from testingDataset.clearing import *

__author__ = 'ama'


def guiFolder():
    """ function void
    Calls   folderCheck()

    """
    path = raw_input("dwse path fakeloy for folder test:")
    if folderCheck(path)[0]:
        print "koble to folder structure"

    else:
        print "exptected"+str(folderCheck(path)[2])+"but got"+str(folderCheck(path)[1])

def guiJpeg():
    """ function void
    Calls   extentionCheck()
    """
    path = raw_input("dwse path fakeloy for extention test:")
    failExtentions = (extentionCheck(path))
    if  len(failExtentions)>0:
        print "yparxoyn lathos extentions stis "+str(failExtentions)

    else:
        print "koble ta file extentions"

def guiImageVal():
    """ function void
    Calls   extentionCheck() for each path given(2)
    """
    pathA,pathB = raw_input("dwse 2 path fakeloy \n mono me photo gia check an einai corrupt:").split()
    pathsList = [pathA,pathB]
    for path in pathsList:
        failImages = checkImage(path)
        if len(failImages)>0:
            print "yparxoyn lathoi stis :" + str(failImages)+"sto fakelo"+str(path)
        else:
            print "Einai valid oles"

def guiDeleteNonJpg():
    path = raw_input("Dwse file path to remove all non jpg files")
    deleteNonJpg(path)

myfunclist = [guiFolder,guiJpeg,guiImageVal,guiDeleteNonJpg]

def checksProg():
    x = raw_input("Your trip just started! \n Press \n 0 for folder structure check \n 1 for extentions check \n"
                  " 2 for valid images in a folder \n 3 to delete all non jpg files \n 4 run all checks \n")
    while 1:
        if int(x) not in [0,1,2,3,4]:
            break
        elif int(x)==4:
            for func in myfunclist:
                func()
            break
        else:
            myfunclist[int(x)]()
            x = raw_input("\n \n ---Continue testing---- \n Press \n 0 for folder structure check \n 1 for extentions check \n "
                          "2 for valid images in a folder \n 3 to delete all non jpg files \n 4 run all checks \n")
       # x = raw_input("continue with same checks \n")

if __name__ == "__main__":
    checksProg()
