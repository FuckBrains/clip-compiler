# main.py

#setup
import os
import requests
import datetime

#function imports
from generalFunctions import videoInfoRefresh, videoNamer, dateOutput, verifyDirectory, jsonUpdate, jsonRead, findDaysDifference, makeMeFolders

videoInfoRefresh(0)

from generalFunctions import videoInfo

from twitchClips import twitchClipCrawler, twitchLinkDL
from redditClips import redditClipCrawler, redditLinkDL
from clipEditor import clipEditor
from uploader import uploadVideo

#main
def main(n, videoInfo):
    makeMeFolders()
    print(videoInfo)
    #variables
    clipSequence = []
    textSequence = []
    date = dateOutput(0)
    exportDirectory = "saved_Clips\\final\\" + videoInfo[n]["category"] + "\\"
    videoDirectory = "saved_Clips\\source_Clips\\" + videoInfo[n]["category"] + "\\" + date + "\\"
    videoInfo = videoInfo[n]

    #main
    verifyDirectory(videoDirectory)
    verifyDirectory(exportDirectory)

    #clip scraping, parsing, and downloading
    if videoInfo["category"] == "streamer":
        clipData = twitchClipCrawler("broadcaster", videoInfo["searchQuery"], videoInfo["lastRun"])
        twitchLinkDL(clipData, videoDirectory, clipSequence, textSequence)

    elif videoInfo["category"] == "subreddit":
        clipData = redditClipCrawler(videoInfo["subcategory"], videoInfo["searchQuery"])
        redditLinkDL(clipData, videoDirectory, clipSequence, textSequence)

    elif videoInfo["category"] == "games":
        clipData = twitchClipCrawler("game", videoInfo["searchQuery"], videoInfo["lastRun"])
        twitchLinkDL(clipData, videoDirectory, clipSequence, textSequence)


    if clipData == 0: # returns if unable to reach server
        print("$ unable to reach server")
        return

    videoName = videoNamer(1)
    clipEditor(clipSequence, textSequence, exportDirectory, videoName)

    #uploadVideo(videoName, n)

    #print("hello")
    #uploadVideo("video.mp4", n)

# while True:
#     for n in range(len(videoInfo)):
#         print("# starting")
#         videoInfoRefresh()
#         if findDaysDifference(videoInfo[n]["lastRun"]) >= videoInfo[n]["daysInBetweenRuns"]:
#             try:
#                 main(n, videoInfo)
#                 print("# main finished running")
#             except Exception as e:
#                 print("$ main function failed")
#                 print(e)
#             else:
#                 jsonUpdate("videoOptionsInfo.json", n, "lastRun", dateOutput(1))
#                 jsonUpdate("videoOptionsInfo.json", n, "timesRun", str(videoInfo[n]["timesRun"] + 1))
#                 print("# json was updated")
#         else:
#             print("$ video has been done too recently")

videoInfoRefresh()
main(0, videoInfo)
