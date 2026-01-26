import zipfile
import os
import json
import numpy as np
import pandas as pd
import datetime
import tkinter as tk
from tkinter import filedialog


###################
# CUSTOMISATION
# these are all the different types of information that Spotify stores, turn them on/off at your leisure
# audiobooks are ignored, songs and episodes can be turned on/off
#
trackNameEnabled = True
# name of the track 
timePlayedEnabled = True
# time listened to each track
timeStampEnabled = True
# timestamp (when the track was started)
artistNameEnabled = True
# name of the artist
albumNameEnabled = True
# name of the album
startReasonEnabled = True
# why the track was started
stopReasonEnabled = True
# why the track stopped
shuffleEnabled = True
# if Shuffle was enabled during the track
skipEnabled = True
# if the track was skipped prematurely
usernameEnabled = False
# username (username)
platformEnabled = False
# platform (Android, Chromecast, iOS, etc)
episodesEnabled = False
# whether to track episode info (also enables show name). 
trackURLEnabled = False
# Spotify's own URL for the track
countryEnabled = False
# list country per track (location that Spotify logged)
userAgentEnabled = False
# list the streaming agent (Safari, Firefox, etc)
offlineEnabled = False
# if the user was offline during the track
incognitoEnabled = False
# if the user was in a private session.
#
################



def processor():
    with zipfile.ZipFile(path, 'r') as dataFiles:
        # need to get rid of or ignore pdf + video file probably here, since it's where the zip is first opened
        names = dataFiles.namelist()
        jsonNames = [a1 for a1 in names if a1.endswith("json")]
        # excludes all the files that don't end in .json
        jsonNames.sort()
        # poorly sorts the files (since it goes alphabetically, - comes before _, so e.g 2019-2020 is processed before 2019_)
        progress = 0
        output = []
        # creates a progress counter and a list for the outputs to go
        # should write an if statement here that skips the whole processing part for testing and in case I want to use the data without re-formatting it
        print("Starting processing, may take a while depending on number of streaming history files")
        for name in jsonNames:
            print((name.split("/"))[1], "\n")
            content = dataFiles.read(name)
            parsedData = json.loads(content)
            progress = progress + 1
            print("Progress is at", progress, "/", len(jsonNames),"\n")
            # counter to visualise progress
            for stream in parsedData:
                fields_to_remove = ["ip_addr", "ip_addr_decrypted", "spotify_episode_uri", "audiobook_title", "audiobook_uri", "audiobook_chapter_uri", "audiobook_chapter_title", "offline_timestamp"]
                for field in fields_to_remove:
                    stream.pop(field, None)
                # removes all the fields that are outside the scope of this program
                if trackNameEnabled == False:
                    stream.pop("master_metadata_track_name", None)
                if timePlayedEnabled == False:
                    stream.pop("ms_played", None)
                if timeStampEnabled == False:
                    stream.pop("ts", None)
                if artistNameEnabled == False:
                    stream.pop("master_metadata_album_artist_name", None)
                if albumNameEnabled == False:
                    stream.pop("master_metadata_album_album_name", None)
                if startReasonEnabled == False:
                    stream.pop("reason_start", None)
                if stopReasonEnabled == False:
                    stream.pop("reason_end", None)
                if shuffleEnabled == False:
                    stream.pop("shuffle", None)
                if skipEnabled == False:
                    stream.pop("skipped", None)
                if usernameEnabled == False:
                    stream.pop("username", None)
                if platformEnabled == False:
                    stream.pop("platform", None)
                if episodesEnabled == False:
                    stream.pop("episode_name", None)
                    stream.pop("episode_show_name", None)
                if trackURLEnabled == False:
                    stream.pop("spotify_track_uri", None)
                if countryEnabled == False:
                    stream.pop("conn_country", None)
                if userAgentEnabled == False:
                    stream.pop("user_agent_decrypted", None)
                if offlineEnabled == False:
                    stream.pop("offline", None)
                if incognitoEnabled == False:
                    stream.pop("incognito_mode", None)
                else:
                    None
                # removes all the unwanted information according to the each of the True/False statements at the document start
                output.append(stream)
            with open('./Data/processed.json', 'w') as a2:
                json.dump(output, a2, ensure_ascii=True, indent=0)
                # takes all the streams in 'output' and dumps them into the 'processed.json' file
    print("Processing complete, beginning analysing \n")
    output.clear()
    # empties the massive list of data
    analyser()
    # calls the analyser to start the next step



def analyser():
    csvEmptier = open('./Data/CSV/formatted.csv', 'w')
    csvEmptier.truncate()
    csvEmptier.close()
    with open('./Data/processed.json', 'r') as processedStreams:
        a3 = processedStreams.read()
        streamList = json.loads(a3)
        # starts the analysation by reloading the json in a different variable
        streamListLength = int((len(streamList)/5))
        # streamList contains every single track from all the json files, this splits it into smaller chunks
        csvList = []
        # this part is split into sections because large enough transfers were causing crashes and memory errors
        print("Starting analyser, this might take a while depending on filesize")
        #
        for stream in range(0,streamListLength):
            singleStream = streamList[stream]
            # selects a single track from the list
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            # splits each element into its own variable, to keep things shorter
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))
            # this long parameter-monster only goes until "platform" for now (missing 7 arguments)        
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=True)
        csvList.clear()
        # clears the list so it doesn't get double-dipped
        print("First stage complete (20%)")
        #
        # larger gaps help with readability during maintenance/creation :)
        #
        for stream in range((streamListLength+1),(streamListLength*2)):
        # repeats the process for 20%+1 to 40% 
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            #
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("Second stage complete (40%)")
        #
        #
        #
        for stream in range(((streamListLength*2)+1),(streamListLength*3)):
        # repeats the process for 40%+1 to 60% 
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            #
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("Third stage complete (60%)")
        #
        #
        #
        for stream in range(((streamListLength*3)+1),(streamListLength*4)):
        # repeats the process for 60%+1 to 80% 
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            #
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("Fourth stage complete (80%)")
        #
        #
        #
        for stream in range(((streamListLength*4)+1),(len(streamList))):
        # repeats the process for 80%+1 to 100% 
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            #
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        #
        mathematician()
        #
        print("Final stage complete \n")

def mathematician():
    print("CSV data stored, starting data comprising. This stage may take a while")
    # this is the part that takes all the data from the CSV and reformats it *again* into chartable data (combines song playtimes, time per day, time per month, time per album (basically just time per x))


# def charter():
# the final function that draws charts
# now that the CSV works, maybe next it's time for data cleanup


# next to-do:
# ex. take all the streams from 2019 and add up the ms_played
# another thing is to find a way to do "unique:" (counter) and then sort the streams into number of x (times listened to, artist appearance, album...)
# next is time per action (per artist, per album)
# then to chart it all in some pretty way
    
    """
        postMath = input("CSV math is complete, do you wish to continue to charting? Y/N: ")
        if postMath == "Y" or postMath == "y":
            mathematician()
            print("Currently unimplemented")
            raise SystemExit
        elif postMath == "N" or postMath == "n":
            print("Exiting")
            raise SystemExit
        else:
            print("Unknown command, exiting")
            raise SystemExit
        """



try:
    os.mkdir('Data')
except FileExistsError:
    None
except PermissionError:
    print("This program is placed in a read-only location and requires write permissions, please relocate \n")
    raise SystemExit
# checks if the Data folder exists, makes one if not, and checks if it has write perms

try:
    os.mkdir('Data/CSV')
except FileExistsError:
    None
# checks if the CSV subfolder exists, makes one if not



print("Your directory contains", os.listdir("./Data/"),"\n")
# lists the elements inside the Data folder (user/debug info)

dataArray = os.listdir("./Data")
# the directory information stored for the checks below

zips = [ax for ax in dataArray if ax.endswith("zip")]
# checks the directory for files with .zip



if 'mySpotifyData.zip' in dataArray:
    fileName = "mySpotifyData.zip"
    print("Correct file found\n")
    # the first file in the directory is the correct zip file
elif len(zips) == 0:
    print("No zip files found, please place it in the Data folder")
    raise SystemExit
elif len(zips) == 1:
    fileName = zips[0]
    print("Attempting to use the misnamed zip file in the Data folder\n")
elif len(zips) > 1:
    prompt = tk.Tk(screenName="Multiple zip files found, please select the zip file manually")
    prompt.withdraw()
    fileName = filedialog.askopenfilename(title=("Please select your streaming history file"), filetypes=[("Zip", '*.zip')])
    # there are multiple zip files in the directory, user has to choose one
else:
    print("Unknown error has occurred, please try again")
    raise SystemExit

path = "./Data/" + fileName
# combines the folder path to make the final path leading to the right file



if os.path.exists('./Data/processed.json') == True:
    overwriteStatus = input('The data file already exists, do you want to overwrite it and begin processing? Y/N: ')
    # checks if the processed.json file already exists, warns user if yes
    if overwriteStatus == "Y" or overwriteStatus == "y":
        print("Overwriting. \n")
        processor()
        # if user wants to ignore previous data and re-process or process new data, starts processor
    elif overwriteStatus == "N" or overwriteStatus == "n":
        # user does not want to overwrite data, asking if skip processing altogether 
        skipProcessor = input('Do you want to skip the processing and begin analysing? Y/N: ')
        print("\n")
        if skipProcessor == "Y" or skipProcessor == "y":
            print("Analysing. \n")
            analyser()
            # user wants to skip processing but wants to analyse existing data
        elif skipProcessor == "N" or skipProcessor == "n":
            raise SystemExit
            # no usecase for now, exiting
    else: 
        print("Unknown command, exiting. \n")
        raise SystemExit
        # user did not follow prompts, exiting
elif os.path.exists('./Data/processed.json') == False:
    processor()
    # in case the file does not exist, skips prompts and starts processor
else:
    print("Unknown error occurred, please check files and try again")
    raise SystemExit
