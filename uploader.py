import httplib2
import json
import time
from os import listdir, getcwd, rename, remove
from os.path import isfile, join, splitext
from shutil import copy
from PIL import Image
from selenium import webdriver
from datetime import datetime, timedelta
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

from generalFunctions import verifyDirectory, videoInfoRefresh

videoInfoRefresh()

from generalFunctions import videoInfo

CLIENT_SECRET = 'client_secret.json'
SCOPE = ['https://www.googleapis.com/auth/youtube.upload']
STORAGE = Storage('credentials.storage')

def authorize_credentials():
    # Fetch credentials from storage
    credentials = STORAGE.get()
    # If the credentials doesn't exist in the storage location then run the flow
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials

def add_logo(mfname, lfname, outfname):
    try:
        mimage = Image.open(mfname)
        limage = Image.open(lfname)
    except:
        print("$ thumbnail or logo image files are missing")
    else:
        # resize logo
        wsize = int(min(mimage.size[0], mimage.size[1]) * 0.25)
        wpercent = (wsize / float(limage.size[0]))
        hsize = int((float(limage.size[1]) * float(wpercent)))

        simage = limage.resize((wsize, hsize))
        mbox = mimage.getbbox()
        sbox = simage.getbbox()

        # right bottom corner
        box = (0, mbox[3] - sbox[3])
        mimage.paste(simage, box)
        mimage.save(outfname)


meta = {  # meta dictionary
    "title": "",
    "description": "",
    "tags": [],
    "thumbnail": "",
    "category_id": "",
    "defaultLanguage": "en_US",
    "notifySubscribers": True
}

def generateMeta(videoInfo, meta):
    if videoInfo["category"] == "subreddit" or videoInfo["category"] == "games":
        # TITLE
        # BEST videoInfo["subcategory"] MOMENTS OF THE WEEK | Month _ firstdayoftheweek , yyyy
        dt = datetime.now()
        startOfWeek = dt - timedelta(days=dt.weekday())

        months_arr = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

        meta["title"] = "BEST " + videoInfo["subcategory"] + " MOMENTS OF THE WEEK | " + str(months_arr[startOfWeek.month-1]) + " " + str(startOfWeek.day) + ", " + str(startOfWeek.year)

        #CATEGORY_ID
        meta["category_id"] = "17" # sports category

    elif videoInfo["category"] == "streamer":
        # TITLE
        # BEST videoInfo["subcategory"] TWITCH MOMENTS #(videoInfo["timesRun"] + 1)
        dt = datetime.now()
        startOfWeek = dt - timedelta(days=dt.weekday())

        meta["title"] = "BEST " + videoInfo["subcategory"].upper() + " MOMENTS " + "#" + str(int(videoInfo["timesRun"]) + 1)

        #CATEGORY_ID
        meta["category_id"] = "20" # gaming category

    # DESCRIPTION
    description_arr = ["🔴 Don't Forget to Like, Comment, and Subscribe 🔴"]
    description_arr.append(meta["title"])

    for i in range(len(description_arr)):
        meta["description"] += description_arr[i]
        meta["description"] += "\n\n"

    # TAGS
    '''
    driver = webdriver.Firefox('D:\Programming\geckodriver')

    driver.get('https://rapidtags.io/generator/')

    #if popup appears exit it
    #if id:'popup-modal' display != none # this is not real code # figure out how to do this
    popup_exit = driver.find_element_by_xpath('//*[@id="popup-modal"]/div/i')
    popup_exit.click()

    # allows popup to close
    time.sleep(5)

    # input title into generator
    input_box = driver.find_element_by_xpath('//*[@id="search"]/div[1]/label/input')
    input_box.send_keys(meta["title"])

    # click submit
    submit_button = driver.find_element_by_xpath('//*[@id="search"]/div[1]/label/i[2]')
    submit_button.click()

    time.sleep(5)

    parent_div = driver.find_element_by_xpath('//*[@id="tag-generator"]/div[1]')
    count_of_divs = len(parent_div.find_elements_by_xpath("./span"))
    for i in range(count_of_divs):
        tag = driver.find_element_by_xpath('//*[@id="tag-generator"]/div[1]/span[' + str(i + 1) + ']')
        meta["tags"].append(tag.text)

    driver.quit()
    '''
    # THUMBNAIL
    cwd = getcwd()
    thumbnail_dir = cwd + '\\images\\thumbnails\\' + videoInfo["category"] + '\\' + videoInfo["subcategory"]
    images_dir = cwd + '\\images\\'


    verifyDirectory(thumbnail_dir)
    verifyDirectory(thumbnail_dir + '\\new_thumbs')
    verifyDirectory(thumbnail_dir + '\\used_thumbs')

    all_new_thumbs = [f for f in listdir(thumbnail_dir + '\\new_thumbs') if isfile(join(thumbnail_dir + '\\new_thumbs', f))]

    while len(all_new_thumbs) == 0:
        print("$ no new thumbnails available for category. please put thumbnails in the " + thumbnail_dir + "\\new_thumbs directory")
        print("# rechecking for thumbnails in 1 minute")
        time.sleep(60)
        all_new_thumbs = [f for f in listdir(thumbnail_dir + '\\new_thumbs') if isfile(join(thumbnail_dir + '\\new_thumbs', f))]

    file_dir = splitext(thumbnail_dir + '\\new_thumbs\\' + all_new_thumbs[0])[0]
    file_ext = splitext(thumbnail_dir + '\\new_thumbs\\' + all_new_thumbs[0])[-1].lower()

    # convert file to jpg
    if(file_ext != '.jpg'):
        im = Image.open(file_dir + file_ext)
        rgb_im = im.convert('RGB')
        rgb_im.save(file_dir + '.jpg')
        remove(file_dir + file_ext)

    if len(all_new_thumbs) > 0:
        #add_logo(file_dir + '.jpg', images_dir + '\\logo_whit.png', images_dir + 'thumbnail.jpg')
        
        try:
            remove(images_dir + 'thumbnail.jpg')
        except:
            copy(file_dir + '.jpg', images_dir + 'thumbnail.jpg')
            #rename(file_dir + '.jpg', images_dir + 'thumbnail.jpg')
            #rename(file_dir + '.jpg', images_dir + 'thumbnail.jpg')

            meta["thumbnail"] = images_dir + 'thumbnail.jpg'

            rename(file_dir + '.jpg', thumbnail_dir + '\\used_thumbs\\' + all_new_thumbs[0]) # + '.jpg')
    else:
        print("# Thumbnail directory is empty, default thumbnail will be used.")


def uploadVideo(video_file_name, n):
    generateMeta(videoInfo[n], meta)

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "CLIENT_SECRET.json"
    credentials = authorize_credentials()

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    print("starting youtube upload process")
    request = youtube.videos().insert(
        part="snippet,status",
        body={
          "snippet":{
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "defaultLanguage": meta["defaultLanguage"],
            "categoryId": meta["category_id"]
          },
          "status": {
            "privacyStatus": "public"
          }
        },
        media_body=MediaFileUpload(video_file_name)
    )
    try:
        response = request.execute()
    except googleapiclient.errors.HttpError:
        print("daily limit reached for youtube API, retrying in 10 minutes")
        while(True):
            time.sleep(600)
            uploadVideo(video_file_name)
    else:
        time.sleep(240) # so that video can load before thumbnail is uploaded
        request = youtube.search().list(
            part="snippet",
            channelId="UCj_HH3WpibKz0hOnGjgj90g",
            maxResults=1,
            order="date"
        )

        try:
            response = request.execute()
            print(response)
        except:
            print("$ error")
        else:
            newVideoId = response["items"][0]["id"]["videoId"]
            request = youtube.thumbnails().set(
                videoId=newVideoId,
                media_body=MediaFileUpload("images/thumbnail.jpg")
            )
            response = request.execute()
			
#uploadVideo("video.mp4", 0)