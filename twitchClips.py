# twitchClips.py

import requests
import urllib
from datetime import datetime
from generalFunctions import videoNamer, clipLength
import json

clipData = [[], []]


# find clips
def twitchClipCrawler(searchType, searchId, lastRun): # searchType = "broadcaster" or "game"
    headers = {
        'Client-ID': 'haatlj3wudnr0bu1o830h4v7r58vj0',
    }
	
    if lastRun != '01/01/0001':
        s = datetime.strptime(lastRun, '%d/%m/%Y').isoformat('T')
        e = datetime.now().isoformat('T')
        
        params = [['first', '100'],
                  ['started_at', s],
                  ['ended_at', e]]
    else:
        params = [['first', '100']]

        
    if searchType == "broadcaster":
        params.append(['broadcaster_id', searchId])

    elif searchType == "game":
        params.append(['game_id', searchId])

    params = tuple(params)


    try:
        r = requests.get('https://api.twitch.tv/helix/clips', headers=headers, params=params)
        clipInfo = r.json()["data"]
    except:
        print("$ could not get clip data. check internet connection or twitch server status")
        return 0
    else:
        for i in range(len(clipInfo)):
            videoLink = clipInfo[i]["thumbnail_url"][38:]
            if videoLink[:2] == "AT":
                videoLink = videoLink.split("-")
                videoLink = videoLink[0] + "-" + videoLink[1]
            else:
                videoLink = videoLink.split("-")[0]

            clipData[0].append("https://clips-media-assets2.twitch.tv/" + videoLink + ".mp4")
            clipData[1].append(clipInfo[i]["title"])

        print(clipData[0])
        print("# finished scraping twitch")
        return clipData

# download clips
def twitchLinkDL(clipData, videoDirectory, clipSequence, textSequence):
    n = 0
    while n < clipLength:
        if checkVideo(len(clipData[1][n]), n) == True:
            try:
                videoName = videoNamer(0)
                urllib.request.urlretrieve(clipData[0][n], videoDirectory + videoName)
                # videoName = videoNamer(0)
            except urllib.error.HTTPError:
                print("# failed to download video")
                clipData[0].pop(n)
                clipData[1].pop(n)
                n -= 1
            else:
                print("# " + videoName + " was downloaded")
                clipSequence.append(videoDirectory + videoName)
                textSequence.append(clipData[1][n])
        else:
            clipData[0].pop(n)
            clipData[1].pop(n)
            n -= 1
        n += 1
    return

def checkVideo(titleLength, n):
    if titleLength > 70:
        print("$ Clip #" + str(n) + " was removed due to video title exceeding 110 characters")
        return False
    else:
        return True
