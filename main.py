import zipfile
import os
import json
import numpy as np
import pandas as pd
from operator import itemgetter


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
    print("Processing complete, beginning analysing")
    output.clear()
    # empties the massive list of data
    analyser()
    # calls the analyser to start the next step



def analyser():
    csvEmptier = open('./Data/formatted.csv', 'w')
    csvEmptier.truncate()
    csvEmptier.close()
    # empties the CSV (REPLACE WITH A BETTER SOLUTION, CURRENTLY CSV CAN ONLY APPEND!!!)
    with open('./Data/processed.json', 'r') as processedStreams:
        a3 = processedStreams.read()
        streamList = json.loads(a3)
        # starts the analysation by reloading the json in a different variable
        streamListLength = int((len(streamList)/5))
        # streamList contains every single track from all the json files, this splits it into smaller chunks
        csvList = []
        #
        for stream in range(0,streamListLength):
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStream.get("ms_played")],"Timestamp":[singleStream.get("ts")],"Artist":[singleStream.get("master_metadata_album_artist_name")],"Album":[singleStream.get("master_metadata_album_album_name")],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))
            # this long parameter-monster only goes until "platform" for now (missing 7 arguments)        
        pd.concat(csvList).to_csv("./Data/formatted.csv", mode='a', index=False, header=True)
        csvList.clear()
        print("First stage complete (0%-20%)")
        #
        # larger gaps help with readability during maintenance/creation :)
        #
        for stream in range((streamListLength+1),(streamListLength*2)):
        # repeats the process for 20%+1 to 40% 
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStream.get("ms_played")],"Timestamp":[singleStream.get("ts")],"Artist":[singleStream.get("master_metadata_album_artist_name")],"Album":[singleStream.get("master_metadata_album_album_name")],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))      
        pd.concat(csvList).to_csv("./Data/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("Second stage complete (20%-40%)")
        #
        #
        #
        for stream in range(((streamListLength*2)+1),(streamListLength*3)):
        # repeats the process for 40%+1 to 60% 
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStream.get("ms_played")],"Timestamp":[singleStream.get("ts")],"Artist":[singleStream.get("master_metadata_album_artist_name")],"Album":[singleStream.get("master_metadata_album_album_name")],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))      
        pd.concat(csvList).to_csv("./Data/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("Third stage complete (40%-60%)")
        #
        #
        #
        for stream in range(((streamListLength*3)+1),(streamListLength*4)):
        # repeats the process for 60%+1 to 80% 
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStream.get("ms_played")],"Timestamp":[singleStream.get("ts")],"Artist":[singleStream.get("master_metadata_album_artist_name")],"Album":[singleStream.get("master_metadata_album_album_name")],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))      
        pd.concat(csvList).to_csv("./Data/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("Fourth stage complete (60%-80%)")
        #
        #
        #
        for stream in range(((streamListLength*4)+1),(len(streamList))):
        # repeats the process for 80%+1 to 100% 
            singleStream = streamList[stream]
            singleStreamName = singleStream.get("master_metadata_track_name")
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Time":[singleStream.get("ms_played")],"Timestamp":[singleStream.get("ts")],"Artist":[singleStream.get("master_metadata_album_artist_name")],"Album":[singleStream.get("master_metadata_album_album_name")],"Start Reason":[singleStream.get("reason_start")],"End Reason":[singleStream.get("reason_end")],"Shuffle":[singleStream.get("shuffle")],"Skipped":[singleStream.get("skipped")],"Username":[singleStream.get("username")],"Platform":[singleStream.get("platform")]}))      
        pd.concat(csvList).to_csv("./Data/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("Final stage complete (80%-100%)")

    
# now to replace the "print" with the actual function (take them and sort them, maybe do song counter first)
# since it's always tied to "master_metadata_track_name":, I can just always search the list and dictionary for that specific key
# dict("master_metadata_track_name")

# need to reformat each dictionary so that they follow "master_metadata_track_name" (or "episode_name" (episode addon later))
# the good thing is that the list won't change, so I can just run the program over and over with a different dictionary key every time on a loop without breaking any data
# so for example, I'd run the song first
# it'd look for "master_metadata_track_name"
# also, it has to have some way to expand this search based on which keys are in each dictionary (episodes, incognito, url... enabled vs disabled)


# ex.
# Sugar (263 plays), 5391035 ms played, Maroon 5 (200 appearances), V (125 appearances)
# ideally formatted in a way that can save files as .csv so they can just be exported to 



# input("All streams processed, would you like to print a .csv file? Y/N: ")

try:
    os.mkdir('Data')
except FileExistsError:
    None
except PermissionError:
    print("This program is placed in a read-only location and requires write permissions, please relocate \n")
    raise SystemExit
# checks if the Data folder exists, makes one if not, and checks if it has write perms



print("Your directory contains", os.listdir("./Data/"),"\n")
# lists the elements inside the Data folder (user/debug info)

dataArray = os.listdir("./Data")

zips = [ax for ax in dataArray if ax.endswith("zip")]

# the directory information stored for the checks below

#
# could change this if check to prompt the user in case more than 1 zip file is found
#

if not dataArray:
    input("Please move your 'my_spotify_data.zip' file to the Data folder.\n")
    # has no files, needs user to move zip there
if 'mySpotifyData.zip' in dataArray:
    fileName = "mySpotifyData.zip"
    print("Correct file found\n")
    # the first file in the directory is the correct zip file
elif len(zips) == 1:
    fileName = zips[0]
    print("Attempting to use the misnamed zip file in the Data folder\n")
elif len(zips) > 1:
    chosenZip = input("Found more than 1 .zip file, which one do you want to use?", zips[0], zips[1], "\n")
    fileName = chosenZip
elif len(dataArray) > 5:
    print("Too many files found in the Data folder, please remove unnecessary files.\n")
    raise SystemExit
    # the correct file wasn't found and too may files are present
else:
    print("Unknown error has occurred, please try again")
    raise SystemExit

path = "./Data/" + fileName
# combines the folder path to make the final path leading to the right file



if os.path.exists('./Data/processed.json') == True:
    overwriteStatus = input('The data file already exists, do you want to overwrite it? Y/N: ')
    # checks if the processed.json file already exists, warns user if yes
    if overwriteStatus == "Y" or overwriteStatus == "y":
        print("\n")
        processor()
        # if user wants to ignore previous data and re-process or process new data, starts processor
    elif overwriteStatus == "N" or overwriteStatus == "n":
        # user does not want to overwrite data, asking if skip processing altogether 
        skipProcessor = input('Do you want to skip the processing and begin analysation? Y/N: ')
        print("\n")
        if skipProcessor == "Y" or skipProcessor == "y":
            print("\n")
            analyser()
            # user wants to skip processing but wants to analyse existing data
        elif skipProcessor == "N" or skipProcessor == "n":
            raise SystemExit
            # no usecase for now, exiting
    else: 
        print("Unknown command, try again. \n")
        raise SystemExit
        # user did not follow prompts, exiting
elif os.path.exists('./Data/processed.json') == False:
    processor()
    # in case the file does not exist, skips prompts and starts processor
else:
    print("Unknown error occurred, please check files and try again")
    None


# next to-do:
# take the now filtered results from processed.json and turn them into full information
# ex. take all the streams from 2019 and add up the ms_played
# another thing is to find a way to do "unique:" (counter) and then sort the streams into number of x (times listened to, artist appearance, album...)
# next is time per action (per artist, per album)
# then to chart it all in some pretty way

"""
if len(dataArray) < 4:
    if ".zip" in os.path.splitext(dataArray[0]):
        fileName = dataArray[0]
        print("Attempting to use the misnamed zip file in the Data folder.\n")
        # checks if the first file is a zip, then uses it if so
    elif ".zip" in os.path.splitext(dataArray[1]):
        fileName = dataArray[1]
        print("Attempting to use the misnamed zip file in the Data folder.\n")
        # checks if the second file is a zip, then uses it if so
    else:
        print("The files found in Data folder do not match the correct type, please move your 'my_spotify_data.zip' file to the Data folder.\n")
        raise SystemExit
        # didn't find a zip file
"""