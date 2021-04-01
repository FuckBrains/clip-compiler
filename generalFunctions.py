import os
import datetime
import requests
import json

# variables
clipLength = 15
# category = ""

universalVolume = 0.75
minTimeLength = 10


def jsonUpdate(file_name, n, key_name, new_value):
    file = open(file_name, "r+")

    try:
        f = json.loads(file.read())

    except:
        print("$ json is incorrectly formatted")

    else:
        f[n][key_name] = new_value
        file = open(file_name, "w")
        json.dump(f, file, indent = 4)

def jsonRead(file_name):
    file = open(file_name, "r")
    try:
        f = json.loads(file.read())
    except:
        print("$ json could not be read")
        return
    else:
        return f


def videoInfoRefresh(n = 1):
    if n == 0:
        global videoInfo
    videoInfo = jsonRead("videoOptionsInfo.json")



def cycleArray(array):
    for n in range(0, len(array)):
        return array[n]


def verifyDirectory(path):
    try:
        os.makedirs(path)
    except:
        print("File path " + path + " was verified to exist.")
        return
    else:
        print("File path " + path + " was created.")
        return

sn = 1
# en = 1
def videoNamer(v):
    global sn
    # global en
    if v == 0: #the video named is a source
        videoName = "Source_Clip_#" + str(sn) + ".mp4" #remove '.mp4' extension
        sn += 1
    if v == 1: #the video named is an export
        videoName = date + "_Final.mp4"
        # videoName = category + "_Final_#" + str(en) + ".mp4"
        # en += 1

    return videoName

def dateOutput(type):
    date = datetime.datetime.now()
    if type == 0:
        return str(date.strftime("%d")) + "_" + str(date.strftime("%m")) + "_" + str(date.strftime("%Y")) + "_" + str(date.strftime("%H")) + str(date.strftime("%M"))

    elif type == 1:
        return str(date.strftime("%d")) + "/" + str(date.strftime("%m")) + "/" + str(date.strftime("%Y"))

def findDaysDifference(date):
    lastDate = date.split("/")

    diff =  (datetime.datetime.now()) - (datetime.datetime(int(lastDate[2]), int(lastDate[1]), int(lastDate[0])))

    return round(diff.total_seconds() / 60 / 60 / 24)
	
def makeMeFolders():
    cwd = os.getcwd()
    f = jsonRead("videoOptionsInfo.json")

    for n in range(len(f)):
        thumbnail_dir = cwd + '\\images\\thumbnails\\' + f[n]["category"] + '\\' + f[n]["subcategory"]

        verifyDirectory(thumbnail_dir)
        verifyDirectory(thumbnail_dir + '\\new_thumbs')
        verifyDirectory(thumbnail_dir + '\\used_thumbs')


date = dateOutput(0)



