import os
import math
import numpy as np
from generalFunctions import verifyDirectory, universalVolume
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from moviepy.video.compositing.concatenate import concatenate_videoclips
# from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
# from moviepy.video.VideoClip import ImageClip, TextClip
# from moviepy.video.fx.all import crop, resize
# from moviepy.decorators import audio_video_fx
from moviepy.editor import *

def captionCreator(clipTitle, videoWidth, videoHeight, duration): #!!!! create a video dimension array that stores clip width and height
    #!!!! attempt to remove excesive variable decleration
    textSequence = []
    rn = 0 # row number
    wn = 0 # word number
    fontsize = 50
    # maxCharPerRow = math.floor(videoWidth/(fontsize/1.5)) #!!!! ONLY GENERATE THIS ONCE
    maxCharPerRow = 40
    captionRow = [""] # array to store title split into multiple lines to fit onto video
    captionWords = (clipTitle.split(" ")) # array stores seperated words from clipTitle into individual array items

    for n in range(len(captionWords)):
        if captionWords[n] == "":
            captionWords.pop(n)

    n = 0
    print(captionWords)
    while n < len(captionWords):
        if captionWords[n][0] == "(" or captionWords[n][0] == "[": # removes everything inbetween brackets
            m = n
            while m < len(captionWords):
                if captionWords[m][len(captionWords[m])-1] == ")" or captionWords[m][len(captionWords[m])-1] == "]":
                    captionWords.pop(m)
                    break
                else:
                    captionWords.pop(m)
        elif captionWords[n] == "|" or captionWords[n] == "-": # removes every term after one of these terms is found
            m = n
            while m < len(captionWords):
                captionWords.pop(m)
        else:
            n += 1


    while wn < len(captionWords):
        if len(captionWords[wn])+len(captionRow[rn])-1 <= maxCharPerRow: # checks if the length of the characters in the current row + characters in the next word + a space (" ") are greater than the limit of characters per line
            captionRow[rn] += captionWords[wn] + " " # adds next word in string to caption row
            wn += 1
        else:
            captionRow.append("") # adds another blank array item so that there is something there when it is referenced
            rn += 1
    for n in range(0, len(captionRow)):
        text = (TextClip(txt = captionRow[n],
                        size = (1920, 1080),
                        color = "white",
                        method = "caption",
                        font = "Arial",
                        fontsize = fontsize
                        )
                        .set_duration(duration)
                        .set_pos((-300, 487 - ((len(captionRow)-1) * (fontsize/2)) + ((fontsize/1.15)*n))) # variable will change by the height of each caption to stack the captions of top each other
                        )
        #print(captionRow[n])
        textSequence.append(text)
    return textSequence

def clipEditor(clipSequence, textSequence, exportDirectory = "", exportName = "render.mp4"): #!!!! attempt to morph clipSequence and clipTitle
    formattedTitle = []
    print("")
    for x in range(0, len(clipSequence)):
        print("# Generating Clip Sequence; " + str((round(((x+1) / len(clipSequence))*1000))/10) + "% Done. (" + str(x+1) + "/" + str(len(clipSequence)) + ")")
        clipSequence[x] = VideoFileClip(clipSequence[x])
        oldSize = clipSequence[x].size
        if clipSequence[x].size != [1920, 1080]: # resizes clip to 1080p
            # potentially crop final clip instead
            if (1920/clipSequence[x].size[0]) < (1080/clipSequence[x].size[1]):
                clipSequence[x] = clipSequence[x].resize(height = 1080)
                clipSequence[x] = clipSequence[x].crop(width = 1920, height = 1080, x_center = clipSequence[x].size[0] / 2, y_center=clipSequence[x].size[1] / 2)
            elif (1920/clipSequence[x].size[0]) > (1080/clipSequence[x].size[1]):
                clipSequence[x] = clipSequence[x].resize(width = 1920)
                clipSequence[x] = clipSequence[x].crop(width = 1920, height = 1080, x_center= clipSequence[x].size[0] / 2, y_center=clipSequence[x].size[1] / 2)
            else:
                clipSequence[x] = clipSequence[x].resize(height = 1080)
            print("# Clip #" + str(x+1) + " was resized to " + str(clipSequence[x].size) + " from (" + str(oldSize[0]) + ", " + str(oldSize[1]) + ")")

        dur = int(clipSequence[x].audio.duration-2)
        volumeFloat = 0

        slice = lambda i: clipSequence[x].audio.subclip(i, i+1).to_soundarray(fps=22000)
        sliceVolume = lambda sliceArray: np.sqrt(((1.0*sliceArray)**2).mean())
        volumes = [sliceVolume(slice(i)) for i in range(0,dur)]
        for i in range(0,dur):
            #if volumes[i] > 0.005:
            volumeFloat += volumes[i]

        clipSequence[x] = clipSequence[x].volumex(universalVolume / (volumeFloat / dur))

        print("# Volume of clip has been multiplied by " + str(volumeFloat))

        formattedTitle.append(CompositeVideoClip(captionCreator(textSequence[x], clipSequence[x].size[0], clipSequence[x].size[1], clipSequence[x].duration))) # size[0] is equal to width
        # print(formattedTitle)

    final_video_clip = concatenate_videoclips(clipSequence)
    final_text_clip = concatenate_videoclips(formattedTitle)
    #print(final_text_clip)

    # logo = (ImageClip("images\\logo.png\\") # adds logo and attributes to 'logo' variable
    #           .set_duration(final_video_clip.duration) # sets time logo appears on screen to that of the length of the video
    #           .resize(height=150)
    #           .set_pos((1690,0))) # (width, height)

    # episodeNumber = (TextClip(txt = "EP. #1", #add global permanent variable later that incriments as a video is made
    #                 size = (1920, 1080),
    #                 color = "black",
    #                 font = "CollegiateHeavyOutline-Medium",
    #                 fontsize = 300
    #                 )
    #                 .set_duration(6)
    #                 .set_pos((-540, -440))
    #                 )

    border = (ImageClip("images\\border.png") # adds logo and attributes to 'logo' variable
            .set_duration(final_video_clip.duration)) # sets time logo appears on screen to that of the length of the video

    outro = VideoFileClip("outro\\TT_outro1.mp4") #make this randomly choose outro everytime  # make array that stores song associated with each outro and sends it to description automatically


    final_video_clip_outro = concatenate_videoclips([final_video_clip, outro])

    #thumbnail = CompositeVideoClip([final_video_clip, logo, episodeNumber])
    final_clip = CompositeVideoClip([final_video_clip_outro, border, final_text_clip])


    # for n in range(0, int(final_clip.duration), 10):
    #     final_clip.save_frame("frame" + str(n) + ".png", t=n)

    # final_clip.save_frame("frame.png", t=5)

    final_clip.write_videofile(exportDirectory + exportName, threads = 4) #, progress_bar = False)


    print("")
    print("# File Saved.")

# clipSequence = ["video.mp4"]
# clipEditor(clipSequence, ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"])
