import zipfile
import os
import json
import numpy as np
import pandas as pd
import datetime
import tkinter as tk
from tkinter import filedialog
import configparser





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
        jsonEmptier = open('./Data/processed.json', 'w')
        jsonEmptier.truncate()
        jsonEmptier.close()
        # empties the processed.json file, this way the method later can use "append", rather than write, so it can be cleared more often
        print("Starting processing, should be done shortly \n")
        fields_to_remove = ["ip_addr", "ip_addr_decrypted", "audiobook_title", "audiobook_uri", "audiobook_chapter_uri", "audiobook_chapter_title", "offline_timestamp"]
        # the base list of information to filter out
        if Config.getboolean("Options", "trackNameEnabled") == False:
            fields_to_remove.append("master_metadata_track_name")
        else:
            None
        if Config.getboolean("Options", "timePlayedEnabled") == False:
            fields_to_remove.append("ms_played")
        else:
            None
        if Config.getboolean("Options", "timeStampEnabled") == False:
            fields_to_remove.append("ts")
        else:
            None
        if Config.getboolean("Options", "artistNameEnabled") == False:
            fields_to_remove.append("master_metadata_album_artist_name")
        else:
            None   
        if Config.getboolean("Options", "albumNameEnabled") == False:
            fields_to_remove.append("master_metadata_album_album_name")
        else:
            None
        if Config.getboolean("Options", "startReasonEnabled") == False:
            fields_to_remove.append("reason_start")
        else:
            None
        if Config.getboolean("Options", "stopReasonEnabled") == False:
            fields_to_remove.append("reason_end")
        else:
            None
        if Config.getboolean("Options", "shuffleEnabled") == False:
            fields_to_remove.append("shuffle")
        else:
            None
        if Config.getboolean("Options", "skipEnabled") == False:
            fields_to_remove.append("skipped")
        else:
            None
        if Config.getboolean("Options", "usernameEnabled") == False:
            fields_to_remove.append("username")
        else:
            None
        if Config.getboolean("Options", "platformEnabled") == False:
            fields_to_remove.append("platform")
        else:
            None
        if Config.getboolean("Options", "episodesEnabled") == False:
            fields_to_remove.append("episode_name")
            fields_to_remove.append("episode_show_name")
        else: 
            None
        if Config.getboolean("Options", "trackURLEnabled") == False:
            fields_to_remove.append("spotify_track_uri")
        else:
            None
        if Config.getboolean("Options", "episodeURLEnabled") == False:
            fields_to_remove.append("spotify_episode_uri")
        else:
            None
        if Config.getboolean("Options", "countryEnabled") == False:
            fields_to_remove.append("conn_country")
        else:
            None
        if Config.getboolean("Options", "userAgentEnabled") == False:
            fields_to_remove.append("user_agent_decrypted")
        else:
            None
        if Config.getboolean("Options", "offlineEnabled") == False:
            fields_to_remove.append("offline")
        else:
            None
        if Config.getboolean("Options", "incognitoEnabled") == False:
            fields_to_remove.append("incognito_mode")
        else:
            None
        # adds all the configurable options into the removeable fields list
        for name in jsonNames:
            # picks a file from the list of json files
            content = dataFiles.read(name)
            # reads the file
            parsedData = json.loads(content)
            # picks out the data from the read file
            progress = progress + 1
            print("Current file:", (name.split("/"))[1], "\n")
            print("Progress is at", progress, "/", len(jsonNames),"\n")
            # counter and file name to visualise progress
            for stream in parsedData:
                for field in fields_to_remove:
                    stream.pop(field, None)                    
                    # removes all the unwanted information according to the each of the config options (config.ini)
                output.append(stream)
                # pushes the current stream's info into the output list
        with open('./Data/processed.json', 'w') as a2:
            json.dump(output, a2, ensure_ascii=True, indent=0)
                # takes all the streams in 'output' and dumps them into the 'processed.json' file
        print("Processing complete, beginning analysing \n")
        analyser()
        # calls the analyser to start the next step



def analyser():
    # the is split into sections because large enough transfers were causing crashes and memory errors (and it took so long it seemed like it'd stalled)
    print("Clearing temp CSV file")
    csvEmptier = open('./Data/CSV/formatted.csv', 'w')
    csvEmptier.truncate()
    csvEmptier.close()
    with open('./Data/processed.json', 'r') as processedStreams:
        a3 = processedStreams.read()
        streamList = json.loads(a3)
        # starts the analysation by reloading the json in a different variable
        streamListLength = int((len(streamList)/5))
        # streamList contains every single track from all the json files, this splits it into 5 smaller chunks
        csvList = []
        print("CSV cleared, starting analyser. This may take a while. \n")
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
            singleStreamStart = singleStream.get("reason_start")
            singleStreamEnd = singleStream.get("reason_end")
            singleStreamShuffle = singleStream.get("shuffle")
            singleStreamSkip = singleStream.get("skip")
            singleStreamUser = singleStream.get("username")
            singleStreamPlatform = singleStream.get("platform")
            singleStreamURL = singleStream.get("spotify_track_uri")
            singleStreamShow = singleStream.get("episode_show_name")
            singleStreamEp = singleStream.get("episode_name")
            singleStreamEpURL = singleStream.get("spotify_episode_uri")
            singleStreamCountry = singleStream.get("conn_country")
            singleStreamAgent = singleStream.get("user_agent_decrypted")
            singleStreamOffline = singleStream.get("offline")
            singleStreamIncognito = singleStream.get("incognito_mode")
            # splits each element into its own variable, to keep lines shorter (vertical > horizontal) in this function, it "skips" empty data in the sense that it adds a column forcebly, but not the data (leaves that column empty)
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Duration":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStreamStart],"End Reason":[singleStreamEnd],"Shuffle":[singleStreamShuffle],"Skipped":[singleStreamSkip],"Username":[singleStreamUser],"Platform":[singleStreamPlatform], "URL": [singleStreamURL], "Show Name": [singleStreamShow], "Episode Name": [singleStreamEp], "E-URL":[singleStreamEpURL], "Country":[singleStreamCountry], "User Agent":[singleStreamAgent], "Offline":[singleStreamOffline], "Incognito":[singleStreamIncognito]}))
            # appends all the information into columns       
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=True)
        csvList.clear()
        # clears the list so it doesn't get double-dipped
        print("20%")
        #
        # larger vertical gaps help with readability during maintenance/creation :)
        #
        for stream in range((streamListLength+1),(streamListLength*2)):
        # repeats the process for 20%+1 to 40% 
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            singleStreamStart = singleStream.get("reason_start")
            singleStreamEnd = singleStream.get("reason_end")
            singleStreamShuffle = singleStream.get("shuffle")
            singleStreamSkip = singleStream.get("skip")
            singleStreamUser = singleStream.get("username")
            singleStreamPlatform = singleStream.get("platform")
            singleStreamURL = singleStream.get("spotify_track_uri")
            singleStreamShow = singleStream.get("episode_show_name")
            singleStreamEp = singleStream.get("episode_name")
            singleStreamEpURL = singleStream.get("spotify_episode_uri")
            singleStreamCountry = singleStream.get("conn_country")
            singleStreamAgent = singleStream.get("user_agent_decrypted")
            singleStreamOffline = singleStream.get("offline")
            singleStreamIncognito = singleStream.get("incognito_mode")
            # splits each element into its own variable, to keep lines shorter (vertical > horizontal) in this function, it "skips" empty data in the sense that it adds a column forcebly, but not the data (leaves that column empty)
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Duration":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStreamStart],"End Reason":[singleStreamEnd],"Shuffle":[singleStreamShuffle],"Skipped":[singleStreamSkip],"Username":[singleStreamUser],"Platform":[singleStreamPlatform], "URL": [singleStreamURL], "Show Name": [singleStreamShow], "Episode Name": [singleStreamEp], "E-URL":[singleStreamEpURL], "Country":[singleStreamCountry], "User Agent":[singleStreamAgent], "Offline":[singleStreamOffline], "Incognito":[singleStreamIncognito]}))
            # appends all the information into columns
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("40%")
        #
        #
        #
        for stream in range(((streamListLength*2)+1),(streamListLength*3)):
        # repeats the process for 40%+1 to 60% 
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            singleStreamStart = singleStream.get("reason_start")
            singleStreamEnd = singleStream.get("reason_end")
            singleStreamShuffle = singleStream.get("shuffle")
            singleStreamSkip = singleStream.get("skip")
            singleStreamUser = singleStream.get("username")
            singleStreamPlatform = singleStream.get("platform")
            singleStreamURL = singleStream.get("spotify_track_uri")
            singleStreamShow = singleStream.get("episode_show_name")
            singleStreamEp = singleStream.get("episode_name")
            singleStreamEpURL = singleStream.get("spotify_episode_uri")
            singleStreamCountry = singleStream.get("conn_country")
            singleStreamAgent = singleStream.get("user_agent_decrypted")
            singleStreamOffline = singleStream.get("offline")
            singleStreamIncognito = singleStream.get("incognito_mode")
            # splits each element into its own variable, to keep lines shorter (vertical > horizontal) in this function, it "skips" empty data in the sense that it adds a column forcebly, but not the data (leaves that column empty)
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Duration":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStreamStart],"End Reason":[singleStreamEnd],"Shuffle":[singleStreamShuffle],"Skipped":[singleStreamSkip],"Username":[singleStreamUser],"Platform":[singleStreamPlatform], "URL": [singleStreamURL], "Show Name": [singleStreamShow], "Episode Name": [singleStreamEp], "E-URL":[singleStreamEpURL], "Country":[singleStreamCountry], "User Agent":[singleStreamAgent], "Offline":[singleStreamOffline], "Incognito":[singleStreamIncognito]}))
            # appends all the information into columns
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("60%")
        #
        #
        #
        for stream in range(((streamListLength*3)+1),(streamListLength*4)):
        # repeats the process for 60%+1 to 80% 
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            singleStreamStart = singleStream.get("reason_start")
            singleStreamEnd = singleStream.get("reason_end")
            singleStreamShuffle = singleStream.get("shuffle")
            singleStreamSkip = singleStream.get("skip")
            singleStreamUser = singleStream.get("username")
            singleStreamPlatform = singleStream.get("platform")
            singleStreamURL = singleStream.get("spotify_track_uri")
            singleStreamShow = singleStream.get("episode_show_name")
            singleStreamEp = singleStream.get("episode_name")
            singleStreamEpURL = singleStream.get("spotify_episode_uri")
            singleStreamCountry = singleStream.get("conn_country")
            singleStreamAgent = singleStream.get("user_agent_decrypted")
            singleStreamOffline = singleStream.get("offline")
            singleStreamIncognito = singleStream.get("incognito_mode")
            # splits each element into its own variable, to keep lines shorter (vertical > horizontal) in this function, it "skips" empty data in the sense that it adds a column forcebly, but not the data (leaves that column empty)
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Duration":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStreamStart],"End Reason":[singleStreamEnd],"Shuffle":[singleStreamShuffle],"Skipped":[singleStreamSkip],"Username":[singleStreamUser],"Platform":[singleStreamPlatform], "URL": [singleStreamURL], "Show Name": [singleStreamShow], "Episode Name": [singleStreamEp], "E-URL":[singleStreamEpURL], "Country":[singleStreamCountry], "User Agent":[singleStreamAgent], "Offline":[singleStreamOffline], "Incognito":[singleStreamIncognito]}))
            # appends all the information into columns        
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("80%")
        #
        #
        #
        for stream in range(((streamListLength*4)+1),(len(streamList))):
        # repeats the process for 80%+1 to 100% 
            singleStreamName = singleStream.get("master_metadata_track_name")
            singleStreamPlaytime = singleStream.get("ms_played")
            singleStreamTimestamp = singleStream.get("ts")
            singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
            singleStreamDate = singleStreamTemp.strftime('%Y-%m-%d')
            singleStreamTime = singleStreamTemp.strftime('%H:%M:%S')
            singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
            singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
            singleStreamStart = singleStream.get("reason_start")
            singleStreamEnd = singleStream.get("reason_end")
            singleStreamShuffle = singleStream.get("shuffle")
            singleStreamSkip = singleStream.get("skip")
            singleStreamUser = singleStream.get("username")
            singleStreamPlatform = singleStream.get("platform")
            singleStreamURL = singleStream.get("spotify_track_uri")
            singleStreamShow = singleStream.get("episode_show_name")
            singleStreamEp = singleStream.get("episode_name")
            singleStreamEpURL = singleStream.get("spotify_episode_uri")
            singleStreamCountry = singleStream.get("conn_country")
            singleStreamAgent = singleStream.get("user_agent_decrypted")
            singleStreamOffline = singleStream.get("offline")
            singleStreamIncognito = singleStream.get("incognito_mode")
            # splits each element into its own variable, to keep lines shorter (vertical > horizontal) in this function, it "skips" empty data in the sense that it adds a column forcebly, but not the data (leaves that column empty)
            csvList.append(pd.DataFrame({"Track":[singleStreamName],"Duration":[singleStreamPlaytime],"Date":[singleStreamDate], "Time": [singleStreamTime],"Artist":[singleStreamArtist],"Album":[singleStreamAlbum],"Start Reason":[singleStreamStart],"End Reason":[singleStreamEnd],"Shuffle":[singleStreamShuffle],"Skipped":[singleStreamSkip],"Username":[singleStreamUser],"Platform":[singleStreamPlatform], "URL": [singleStreamURL], "Show Name": [singleStreamShow], "Episode Name": [singleStreamEp], "E-URL":[singleStreamEpURL], "Country":[singleStreamCountry], "User Agent":[singleStreamAgent], "Offline":[singleStreamOffline], "Incognito":[singleStreamIncognito]}))
            # appends all the information into columns        
        pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=False)
        csvList.clear()
        print("Analysing complete \n")
        #
        mathematician()
        #
 


def mathematician():
    print("Reforming data and calculating final numbers.")
    csvData = pd.read_csv('./Data/CSV/formatted.csv')
    if Config.getboolean("Options", "tracknameenabled") == True:
        # if the config is set to save tracks, but not episodes
        csvGrouped = csvData.groupby(["Track", "Album"])
        pd.concat(csvGrouped).to_csv("./Data/CSV/grouped.csv", mode='a', index=False, header=False)
        # this doesn't actually work, the data type is a tuple, concat only works for series and dataframes

    elif Config.getboolean("Options", "tracknameenabled") == False and Config.getboolean("Options", "episodesenabled") == True:
        # if the config is set to save episodes, but not tracks
        csvGroupedEpisodes = csvData.groupby(["Episode Name", "Show Name"])
        pd.concat(csvGroupedEpisodes).to_csv("./Data/CSV/grouped.csv", mode='a', index=False, header=False)

    elif Config.getboolean("Options", "tracknameenabled") == True and Config.getboolean("Options", "episodesenabled") == True:
        # if the config is set to save both episodes and tracks
        csvGroupedBoth = csvData.groupby(["Track", "Album", "Episode Name", "Show Name"])
        pd.concat(csvGroupedBoth).to_csv("./Data/CSV/grouped.csv", mode='a', index=False, header=False)

    elif Config.getboolean("Options", "tracknameenabled") == False and Config.getboolean("Options", "episodesenabled") == False:
        # if the config has both episodes and tracks disabled (thus nothing to sort by)
        print("Config file contains contradiction, please double-check that tracknameenabled and episodesenabled aren't both off and try again.")
        raise SystemExit
    

    # this is the part that takes all the data from the CSV and reformats it *again* into chartable data (combines song playtimes, time per day, time per month, time per album (basically just time per x))

# basic idea is:
# you have a song, x, which comes from album y
# you add it to a list with some array function, listing all its properties (ms_played, time, date...)
# if x AND y already exist, it instead adds up the properties (ms_played = ms_played + ms_played type, for others it should not count the times (artist should always be same, if you cross-check album and song, it can't be a different one,
# but count start reasons, end reasons, list all the dates))
# it should look something like 

# basically have to make a list of a list, where each sublist is a song of its own, sorted by name + album
"""
Song X:
Artist Z
Album Y
Time Listened to: 5399214ms (then convert to s later, to get more consistent results (I imagine statsFM does the opposite, leading to insane rounding errors)
Start Reasons: 21x A, 14x B, 9x C
End Reasons: 30x D, 5x E, 1x F
Shuffles: 50x Yes, 10x No
Skip: 39x Yes, 29x No
Username: just count if it has any different ones
Platform: ^
episode name (same as song name, shouldn't ever duplicate?), can check if the boolean is on whether to even activate
url (only list once, should always be the same?)
episode url (^)
country: list if different ones, if same just ignore count
offline: count I guess (if 0 then ignore)
incognito: ^


something like
if song == existing song
    if song's album == new
        make a new input into list
    if song's album == exists with that song
        add it to the list


"""

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



# print("Your directory contains", os.listdir("./Data/"),"\n")
# lists the elements inside the Data folder (user/debug info), disabled

dataArray = os.listdir("./Data")
# stores the directory for use later

zips = [zipP for zipP in dataArray if zipP.endswith("zip")]
# checks the directory for files with .zip, used to select the zip file

Config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True, )
Config.read('./config.ini')
# this opens the config file, letting the program read it later on



if Config.getboolean("FirstTimer", "firstTimeUser") == True:
    print("Welcome, first time user! Here's some information regarding this tool: \n")
    print("On the first run of this program, it will run through every step, since there is no intermediary data available.")
    print("On subsequent runs, you will be able to skip steps depending on what you want to do with the streaming data.")
    configInput = input("Have you configured the options in the config.ini file yet? Y/N")
    if configInput == "Y" or configInput == "y":
        print("Proceeding with configured options")
        # processor()
        # has selected desired options, starts data processing
    elif configInput == "N" or configInput == "n":
        defaults = input("Would you like to continue with default settings? Y/N:")
        if defaults == "Y" or defaults == "y":
            print("Proceeding with default options")
            # processor()
        elif defaults == "N" or defaults == "n":
            print("Please go configure your desired options, then open the program again")
            raise SystemExit
            # could also find a way to GUI-interactively go through each setting to explain them
    else:
        print("Unknown command, please try again")
        raise SystemExit
    Config['FirstTimer']['firstTimeUser'] = 'False'
    with open('./config.ini', 'w') as configFile:
        Config.write(configFile)
    # informs user on program usage and swaps the config file boolean to false, so the new user prompt doesn't show up again
else:
    None
# quick check to see if this is the first time using program, gives info if yes



if 'mySpotifyData.zip' in dataArray:
    path = "mySpotifyData.zip"
    print("Correct file found\n")
    # the first file in the directory is the correct zip file
elif len(zips) > 0 or len(zips) == 1:
    path = filedialog.askopenfilename(title=("Please select your streaming history file"), filetypes=[("Zip", '*.zip')])
    # there is at least one zip file in the directory, user has to choose one
elif len(zips) == 0:
    print("No zip files found, please move it to the Data folder and try again")
    raise SystemExit
else:
    print("Unknown error has occurred with zip file selection, please check files and try again")
    raise SystemExit



if os.path.exists('./Data/processed.json') == True:
    if Config.getboolean("Function", "alwaysSkipProcessing") == True:
        # if the config setting for skipping processor is on, prompts to skip to analyser
        if Config.getboolean("Function", "alwaysSkipAnalysing") == True:
            # if both the processing and analysing are set to skip, moves to math section
            print("Skipping processing and analysing, starting stat thing")
            mathematician()
        else:
            print("Skipping processing, starting analyser")
            analyser()
        # if the config setting for skipping processor is on, 
    elif Config.getboolean("Function", "alwaysSkipProcessing") == False:
        overwriteStatus = input('The data file already exists, do you want to overwrite it and begin processing? Y/N: ')
        # checks if the processed.json file already exists and checks config status, warns user if yes
        if overwriteStatus == "Y" or overwriteStatus == "y":
            print("Overwriting. \n")
            processor()
            # if user wants to ignore previous data and re-process or process new data, starts processor
        elif overwriteStatus == "N" or overwriteStatus == "n":
            # user does not want to overwrite data, asking if skip processing altogether 
            skipProcessor = input('Do you want to skip the initial data processing? Y/N: ')
            print("\n")
            if skipProcessor == "Y" or skipProcessor == "y":
                if Config.getboolean("Function", "alwaysSkipAnalysing") == True:
                    print("Skipping analyser, ")
                    mathematician()
                    # anaylse skip is enabled in config, automatically enters math phase
                else:
                    print("Analysing. \n")
                    analyser()
                    # user wants to skip processing but wants to analyse existing data
            elif skipProcessor == "N" or skipProcessor == "n":
                raise SystemExit
                # wants to not overwrite data, but doesn't want to skip processing either, exit
        else: 
            print("Unknown command, exiting. \n")
            raise SystemExit
            # user did not follow prompts, exiting
elif os.path.exists('./Data/processed.json') == False:
    processor()
    # in case the file does not exist, skips prompts and starts processor (first time or has no data)
else:
    print("Unknown error occurred, please check files and try again")
    raise SystemExit