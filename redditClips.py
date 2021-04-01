# redditClips.py
# responsible for finding and downloading all reddit clips


import praw
import urllib.request
import requests
import youtube_dl
import json
from generalFunctions import verifyDirectory, videoNamer, clipLength


def redditClipCrawler(subreddit, query, time_filter = 'week'):
    # add login information to .nfo file
    reddit = praw.Reddit(client_id='HNvr9jxX25oLYg',
                         client_secret='TRZ76WtOjvGd4jvgiGaIiiYQZ0c',
                         user_agent='clipCrawler script created by u/ClipCrawler')

    clipData = [[], []]

    print("# starting reddit scrape")
    try:
        for submission in reddit.subreddit(subreddit).search(query, sort="top", syntax="lucene", time_filter=time_filter, limit=250):
            clipData[0].append(submission.url)
            clipData[1].append(submission.title)
    except:
        print("$ reddit could not be reached. check internet connection or reddit server status")
        print("")
        return 0
    else:
        print("# finished scraping reddit")
        print("")
        print(clipData[0])
        return clipData


def redditLinkDL(clipData, videoDirectory, clipSequence, textSequence):
    n = 0
    while n < clipLength:
        try:
            link = clipData[0][n]
            title = clipData[1][n]
        except IndexError:
            print("unable to find " + str(clipLength) + " clips. there were " + str(n) + " clips found.")
            return
        else:
            #removes link prefix
            if link[:8] == "https://":
                #print("# link starts with 'https://'")
                linkMod = link[8:]
            elif link[:7] == "http://":
                #print("# link starts with 'http://'")
                linkMod = link[7:]
            if linkMod[:4] == "www.":
                linkMod = linkMod[4:]

            #streamable
            if linkMod[:10] == "streamable":
                shortcode = linkMod[14:]
                try:
                    video_json = requests.get(url = "https://api.streamable.com/videos/" + shortcode).json()
                except json.decoder.JSONDecodeError: # ensures that files that are unable to be downloaded are not downloaded
                    print("JSON could not be read.")
                    clipData[0].pop(n)
                    clipData[1].pop(n)
                    n -= 1
                else:
                    if checkVideo(video_json["files"]["mp4"]["duration"], len(title), n) == True:
                        videoName = videoNamer(0)
                        urllib.request.urlretrieve("https:" + video_json["files"]["mp4"]["url"], videoDirectory + videoName)
                        print("# " + videoName + " was downloaded")
                        clipSequence.append(videoDirectory + videoName)
                        textSequence.append(title)
                    else:
                        clipData[0].pop(n)
                        clipData[1].pop(n)
                        n -= 1
            #youtube
            elif linkMod[:7] == "youtube":
                ydl_opts = {}
                ydl = youtube_dl.YoutubeDL(ydl_opts)

                with ydl:
                    results = ydl.extract_info(link, download=False)

                if checkVideo(results["duration"], len(title), n) == True:
                    videoName = videoNamer(0)
                    print(videoDirectory)
                    print(videoName)
                    ydl_opts = {'outtmpl': videoDirectory + videoName}
                    ydl = youtube_dl.YoutubeDL(ydl_opts)
                    with ydl:
                        ydl.download([link])

                    print("# " + videoName + " was downloaded")
                    clipSequence.append(videoDirectory + videoName)
                    textSequence.append(title)
                else:
                    clipData[0].pop(n)
                    clipData[1].pop(n)
                    n -= 1
            #unsupported link
            else:
                print("$ link type not supported")
                clipData[0].pop(n)
                clipData[1].pop(n)
                n -= 1
        n += 1
    return

def checkVideo(videoLength, titleLength, n):
    if videoLength > 30:
        print("$ Clip #" + str(n) + " was removed due to length exceeding 30s")
        return False
    elif titleLength > 70:
        print("$ Clip #" + str(n) + " was removed due to video title exceeding 110 characters")
        return False
    elif videoLength < 7:
        print("$ Clip #" + str(n) + " was removed due to length below 7s")
        return False
    else:
        return True
