import zipfile, os, json, datetime, queue, threading, configparser, time
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from collections import Counter



### Raw JSON Processor ###



def processor():
    """Function that takes the raw .zip file containing several JSON fiels and turns into a single, configurable JSON file"""

    with zipfile.ZipFile(zipPath, 'r') as dataFiles:
        # opens the zip file via pre-determined path

        names = dataFiles.namelist()
        # takes each json file individually
        jsonNames = [a1 for a1 in names if a1.endswith("json")]
        # excludes all the files that don't end in .json
        jsonNames.sort()
        # poorly sorts the files (since it goes alphabetically, - comes before _, so e.g 2019-2020 is processed before 2019_)

        output = []
        # creates a progress counter and a list for the outputs to go

        if os.path.exists("./Data/processed.json"):
            # checks if the processed file exists yet
            jsonEmptier = open('./Data/processed.json', 'w')
            jsonEmptier.truncate()
            jsonEmptier.close()
            # opens, adds "nothing" and closes the processed file

        print("Starting processing, should be done shortly \n")
        # user inform

        fields_to_remove = ["ip_addr", "ip_addr_decrypted", "audiobook_title", "audiobook_uri", "audiobook_chapter_uri", "audiobook_chapter_title", "offline_timestamp", "conn_country"]
        # the base list of information to filter out (there is borderline no reason to keep any of these - audiobooks are deprecated and only show up on extremely old data)

        if not Config.getboolean("Options", "track_Name_Enabled"):
            # if track names are disabled, removes track names and album names
            fields_to_remove.append("master_metadata_track_name")
            fields_to_remove.append("master_metadata_album_album_name")

        if not Config.getboolean("Options", "time_Played_Enabled"):
            fields_to_remove.append("ms_played")

        if not Config.getboolean("Options", "timestamp_Enabled"):
            fields_to_remove.append("ts")

        if not Config.getboolean("Options", "artist_Name_Enabled"):
            fields_to_remove.append("master_metadata_album_artist_name")

        if not Config.getboolean("Options", "start_Reason_Enabled"):
            fields_to_remove.append("reason_start")

        if not Config.getboolean("Options", "stop_Reason_Enabled"):
            fields_to_remove.append("reason_end")

        if not Config.getboolean("Options", "shuffle_Enabled"):
            fields_to_remove.append("shuffle")

        if not Config.getboolean("Options", "skip_Enabled"):
            fields_to_remove.append("skipped")

        if not Config.getboolean("Options", "username_Enabled"):
            fields_to_remove.append("username")

        if not Config.getboolean("Options", "platform_Enabled"):
            fields_to_remove.append("platform")

        if not Config.getboolean("Options", "track_URL_Enabled"):
            fields_to_remove.append("spotify_track_uri")

        if not Config.getboolean("Options", "episodes_Enabled"):
            # if episodes are disabled, removes episode names (and show names)
            fields_to_remove.append("episode_name")
            fields_to_remove.append("episode_show_name")

        if not Config.getboolean("Options", "episode_URI_Enabled"):
            fields_to_remove.append("spotify_episode_uri")

        if not Config.getboolean("Options", "user_Agent_Enabled"):
            fields_to_remove.append("user_agent_decrypted")

        if not Config.getboolean("Options", "offline_Enabled"):
            fields_to_remove.append("offline")

        if not Config.getboolean("Options", "incognito_Enabled"):
            fields_to_remove.append("incognito_mode")

        jsonLength = len(names)
        # counts how many files there are in the zip file

        progress = 1
        # sets a counter for progress to 1

        for name in jsonNames:
            # goes through json files 1-by-1

            progress += 1
            # adds 1 to counter
            content = dataFiles.read(name)
            # reads the file
            parsedData = json.loads(content)
            # picks out the data from the read file
            percent = int(progress / jsonLength * 100)
            # calculates the percentage of progress
            print(f"Progress at: {percent}%")
            # sends percentage progress to help visualise

            for stream in parsedData:
                # goes through each individual stream in the loaded json file
                for field in fields_to_remove:
                    # takes a field from the list of fields to get rid of
                    stream.pop(field, None)
                    # and removes that field from each stream

                output.append(stream)
                # pushes the current stream's info into the output list

        with open('./Data/processed.json', 'w') as jsonDone:
            # opens the processed file in write mode
            json.dump(output, jsonDone, ensure_ascii=True, indent=0)
                # takes all the streams in 'output' and dumps them into the 'processed.json' file

        print("JSON file processing complete")
        # finishes work and checks if user wants to continue

        if Config.getboolean("DSI", "dsi_Export"):
            # if DSI is enabled in config
            print("DSI export enabled, proceeding")
            # user inform and immediate next task
            analyserStarter()

        else:
            continueToAnalyser = input("Do you wish to continue to analysing? Y/N: ")
            if continueToAnalyser == "y" or continueToAnalyser == "Y":
                analyserStarter()
            else:
                print("Exiting")
                raise SystemExit



### JSON -> Formatted CSV "Analyser" ###



def analyser(start, end, streamList, enableHeader=False):
    """Function that takes the processed json file and turns them into a formatted CSV file"""
    
    csvList = []
    # makes an empty list to store items in
   
    for stream in range(start, end):
        # for every stream in the set range (by chunk)
        singleStream = streamList[stream]
        # each stream is one from the list
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
        singleStreamSkip = singleStream.get("skipped")
        singleStreamUser = singleStream.get("username")
        singleStreamPlatform = singleStream.get("platform")
        singleStreamURL = singleStream.get("spotify_track_uri")
        singleStreamShow = singleStream.get("episode_show_name")
        singleStreamEp = singleStream.get("episode_name")
        singleStreamEpURL = singleStream.get("spotify_episode_uri")
        singleStreamAgent = singleStream.get("user_agent_decrypted")
        singleStreamOffline = singleStream.get("offline")
        singleStreamIncognito = singleStream.get("incognito_mode")
        # grabs all the different information types the CSV has
        
        csvList.append(pd.DataFrame({
            "Track": [singleStreamName],
            "Duration": [singleStreamPlaytime],
            "Date": [singleStreamDate],
            "Time": [singleStreamTime],
            "Total Time": [singleStreamPlaytime],
            "Artist": [singleStreamArtist],
            "Album": [singleStreamAlbum],
            "Start Reason": [singleStreamStart],
            "End Reason": [singleStreamEnd],
            "Shuffle": [singleStreamShuffle],
            "Skipped": [singleStreamSkip],
            "Username": [singleStreamUser],
            "Platform": [singleStreamPlatform],
            "URI": [singleStreamURL],
            "Show Name": [singleStreamShow],
            "Episode Name": [singleStreamEp],
            "E-URL": [singleStreamEpURL],
            "User Agent": [singleStreamAgent],
            "Offline": [singleStreamOffline],
            "Incognito": [singleStreamIncognito]
        }))
        
    pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=enableHeader)
    # pushes the list into the CSV (in append mode, since it gets cleared before call - this way it can be split in task)
    print(f"Processed CSV lines: {start:,.0f} - {(end - 1):,.0f}")
    # prints the completed point



### Analyser Starter Function ###



def analyserStarter():
    """Small function that calculates start/end points for Analyser and runs it if conditions are met"""

    if os.path.exists('./Data/CSV/formatted.csv'):
        # if the formatted.csv file already exists
        print("Clearing CSV file\n")
        # user inform
        csvEmptier = open('./Data/CSV/formatted.csv', 'w')
        csvEmptier.truncate()
        csvEmptier.close()
        # opens the csv, writes nothing (effectively deleting everything), then closing the file

        with open('./Data/processed.json', 'r') as processedStreams:
            # opens the processed.json file
            processedContent = processedStreams.read()
            # stores the processed file inside a variable
            streamList = json.loads(processedContent)
            streamListLength = len(streamList)
            # gets the list length
            streamListChunk = (streamListLength // 10)
            print(f"CSV split into 10 chunks, each chunk contains {streamListChunk:,.0f} lines\n")
            # splits the length into 10 equal (integer) chunks (/ = float, // = int) (helps with memory and user inform)

            for chunk in range(10):
                # for every chunk between 0 and 9 (since CSV gets split into 10 parts)

                startPoint = (chunk * streamListChunk)
                # start point is always the current chunk * the length of a chunk

                if chunk == 9:
                    # on the last chunk, uses a bit of a different process
                    endPoint = streamListLength
                    # uses the list length to process *all* lines
                else:
                    endPoint = ((chunk + 1) * streamListChunk)
                    # end point is always the next chunk from startpoint
                
                enableHeader = (chunk == 0)
                # enables the header only for the first chunk

                analyser(startPoint, endPoint, streamList, enableHeader)
                # passes the start and end points, as well as the list to process 
    
                print(f"Progress: {(chunk + 1) * 10}%")

            print("CSV formatted")

            if Config.getboolean("DSI", "dsi_Export"):
                # if DSI is enabled in config
                print("DSI export enabled, proceeding")
                # user inform and immediate next task
                mathematician()

            else:
                continueToMathematician = input("Do you wish to continue to CSV grouping? Y/N: ")
                if continueToMathematician == "y" or continueToMathematician == "Y":
                    mathematician()
                else:
                    print("Exiting")
                    raise SystemExit
 


### Counter ###

def counter(fakeList):
    """Helper function that turns requested list into a pandas series to drop "nan" values, then turns back into a list"""
    return dict(Counter(list(pd.Series(fakeList).dropna())))
    # is called by mathematician to dynamically count the grouped data's aggregate values


### Mathematician (formatted.csv -> grouped.csv/dsi.csv) ###



def mathematician():
    """Function to turn the formatted CSV files into grouped, data-calculated CSVs"""

    print("Combining indices and calculating final numbers\n")

    csvData = pd.read_csv('./Data/CSV/formatted.csv')
    # opens the formatted.csv file as csvData

    if Config.getboolean("Options", "track_Name_Enabled") and not Config.getboolean("DSI", "dsi_Export"):
        # if the config is set to save tracks, and DSI is not on
        csvData.set_index(["Track", "Artist", "Album"])
        # sets a multi-index to track, artist and album
        csvGrouped = csvData.groupby(["Track", "Artist", "Album"]).agg({"Duration": list, "Date": list, "Time": list, "Total Time": sum, "Start Reason": counter, "End Reason": counter, "Shuffle": counter, "Skipped": counter, "Username": counter, "Platform": counter, "URI": counter, "Country": counter, "User Agent": counter, "Offline": counter, "Incognito": counter})
        # combines all occurances of a track that has the same name, artist and album into one multi-index - creates a dictionary for most pieces of info, except duration, which it sums up (as milliseconds)
        print("CSV data grouped, calculating playcounts\n")
        playcountList = []
        # makes an empty list
        for i, x in csvGrouped.iterrows():
            # i contains the actual "identifier" of the track (track, artist, album)
            playdates = csvGrouped.loc[i, "Date"]
            # takes the list of dates for each track
            playcount = len(playdates)
            # stores the length of each track's date list (easy way to count playcount)
            playcountList.append(playcount)
            # adds the playcount into the list
        csvGrouped.insert(0, "Playcount", playcountList)
        # after all tracks are done and the for loop ends, inserts a new column containing the playcount for each track
        csvGrouped.to_csv('./Data/CSV/grouped.csv', index=True)
        # pushes the whole modified dataframe into a csv file
        print("Playcounts calculated, data stored\n")

    if Config.getboolean("DSI", "dsi_Export"):
        # if the config setting for DSI exporting is enabled
        csvData.set_index("Track", inplace=True)
        # sets the CSV index to "track"
        csvDiscord = csvData.groupby(["Track"]).agg({"Artist": "first", "Album": "first", "Duration": list, "Date": list, "Time": list, "Total Time": sum, "URI": lambda x: list(set(x))})
        # stores the csvData as a groupby of just the track (this is what DSI requires to function)

        csvDiscord["Playcount"] = csvDiscord["Date"].apply(len)
        # calculates the length of "Date" list per column and saves it as "Playcount" column
        columns = ["Playcount"] + [col for col in csvDiscord.columns if col != "Playcount"]
        # automatically moves the "Playcount" column to the first position
        csvDiscord = csvDiscord[columns]
        # after all tracks are done and the for loop ends, inserts a new column containing the playcount for each track

        csvDiscord = csvDiscord.explode("URI")
        # "explodes" the CSV (takes all the cells with multiple URIs and splits them with identical data)
        csvDiscord.set_index("URI", inplace=True)
        # sets the index to URI
        csvDiscord.to_csv('./Data/CSV/dsi.csv', index=True)
        # pushes the whole modified dataframe into a CSV file, now with URI as index
        print("DSI CSV exported\n")
        # user prompt

    print("Mathematician done, exiting in 5 seconds\n")
    # nothing added yet, exits
    time.sleep(5)
    raise SystemExit
        
"""
        # pd.concat(csvGrouped).to_csv("./Data/CSV/grouped.csv", mode='a', index=False, header=False)
        # this doesn't actually work, the data type is a tuple, concat only works for series and dataframes
    else:
        print("Failed at some point, fix this")
        # currently commented other options, will write this first
    
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
"""


def summary():
    if os.path.exists('./Data/CSV/formatted.csv'):
        csvData = pd.read_csv('./Data/CSV/formatted.csv')
        csvData
        # this takes the grouped data and makes a quick summary (top 10/50 songs, total playtime, playtime per month?)
        # playtime per timeperiod requires something where it finds the year/month and then stores the list number, then takes all the playtime for those indices


# basic idea is:
# you have a song, x, which comes from album y
# you add it to a list with some array function, listing all its properties (ms_played, time, date...)
# if x AND y already exist, it instead adds up the properties (ms_played = ms_played + ms_played type, for others it should not count the times (artist should always be same, if you cross-check album and song, it can't be a different one)
# count start reasons, end reasons, shuffles, skips... also list all the times and dates))

# basically have to make a list of a list, where each sublist is a song of its own, sorted by name + album
"""
Song X:
Artist Z
Album Y
Time Listened to: 5399214ms (then convert to s later, to get more consistent results (I imagine statsFM does the opposite, leading to insane rounding errors)
Start Reasons: 21x A, 14x B, 9x C
End Reasons: 30x D, 5x E, 1x F
Shuffles: 50x Yes
Skip: 39x Yes
Username: just count if it has any different ones (unique)
Platform: (unique)
episode name (same as song name, shouldn't ever duplicate?), can check if the boolean is on whether to even activate
url (only list once, should always be the same?)
episode url (^)
country: list if different ones, if same just ignore count
offline: count I guess (if 0 then ignore)
incognito: ^



def charter():
# the final function that draws charts from the finalised data
    

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



### Permission Check ###

try:
    os.mkdir('Data')
    # tries to create a Data folder
except FileExistsError:
    # if the folder already exists (as it should), does nothing
    None
except PermissionError:
    # if the folder can't be made (permission error), prompts user and exits
    print("This program is placed in a read-only location and requires write permissions, please relocate\n")
    time.sleep(10)
    raise SystemExit



### Setup ###



dataArray = os.listdir("./Data")
# stores the directory

zips = [zipP for zipP in dataArray if zipP.endswith("zip")]
# checks the directory for files with .zip, used to select the zip file

Config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
Config.read('./config.ini')
# this opens the config file to be checked later


# Zip file selector
if 'mySpotifyData.zip' in dataArray:
    zipPath = "mySpotifyData.zip"
    print("Correct file found\n")
    # the first file in the directory is the correct zip file (default name)
elif len(zips) == 1:
    zipPath = "./Data/" + zips[0]
    print("Using misnamed zip file\n")
    # there is a zip file, but not named "mySpotifyData", uses that (may cause issues if a zip file of the wrong type is placed in the folder)
elif len(zips) > 1:
    zipPath = filedialog.askopenfilename(title=("Please select your streaming history file"), filetypes=[("Zip", "*.zip")])
    # there is more than one zip file in the directory, user has to choose one
elif len(zips) == 0:
    print("No zip files found, please move it to the Data folder and try again\n")
    raise SystemExit
    # no valid (zip) files in the Data folder
else:
    print("Unknown error has occurred with zip file selection, please check files and try again\n")
    raise SystemExit
    # shouldn't ever happen, but exits the program rather than erroring out


# logic for determining which task should start
if os.path.exists('./Data/processed.json'):
    # if the processed file exists (meaning this program has been run at least once)

    if Config.getboolean("Function", "always_Skip_Processing"):
        # if the config setting for skipping processor is True, prompts to skip to analyser
        print("The config option to skip processing is enabled, skipping processing")
        
        if Config.getboolean("Function", "always_Skip_Analysing"):
            # if both the processing and analysing are set to skip, moves to math section
            print("The config option to skip analyser is enabled, skipping analysing")
            print("Starting math thing")
            mathematician()
        else:
            # if the config setting for skipping processor is on, but the analysation setting is off, starts analyser
            print("Skipping processing, starting analyser")
            analyserStarter()

    else:
        # if the config setting to skip processing is False
        overwriteStatus = input('The data file already exists, do you want to overwrite it and begin processing? Y/N: ')
        # checks if the processed.json file already exists and checks config status, warns user if yes

        if overwriteStatus == "Y" or overwriteStatus == "y":
            # if the prompt is yes 
            print("Overwriting. \n")
            processor()
            # if user wants to ignore previous data and re-process or process new data, starts processor

        elif overwriteStatus == "N" or overwriteStatus == "n":
            skipProcessor = input('Do you want to skip the initial data processing? Y/N: ')
            # user does not want to overwrite data, asking if skip processing altogether

            if skipProcessor == "Y" or skipProcessor == "y":
                if Config.getboolean("Function", "always_Skip_Analysing") == True:
                    print("Skipping processing and analysing, starting mathematician")
                    mathematician()
                    # anaylser skip is enabled in config, automatically enters math phase
                else:
                    skipAnalyser = input('Do you want to skip the data analysation and start data reformatting? Y/N:')
                    if skipAnalyser == "Y" or skipAnalyser == "y":
                        print("Skipping processing and analysing, starting mathematician")
                        mathematician()
                        # manual method to skip processing and analysing via input chain
                    else:
                        print("Analysing. \n")
                        analyserStarter()
                        # user wants to skip processing but wants to analyse existing data
            elif skipProcessor == "N" or skipProcessor == "n":
                raise SystemExit
                # wants to not overwrite data, but doesn't want to skip processing either, exit
        else: 
            print("Unknown command, exiting. \n")
            raise SystemExit
                # user did not follow prompts, exiting


elif not os.path.exists('./Data/processed.json'):
    # in case the file does not exist

    if Config.getboolean("DSI", "dsi_Export"):
        # in case the file does not exist, and DSI is enabled
        print("No processed file found, DSI is enabled, processing data to fit DSI requirements")
        processor()
    else:
        print("No processed file found, starting program from the beginning")
        processor()

else:
    print("Unknown error occurred, please check files and try again")
    raise SystemExit
    # shouldn't ever happen, but exits the program rather than erroring out