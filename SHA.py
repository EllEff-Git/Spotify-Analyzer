import zipfile, os, json, datetime, configparser, time
import numpy as np
import pandas as pd
import easygui
import tkinter as tk
from collections import Counter


SHAver = "v0.20.2.0420"



### Stage 1: Raw JSON Processor ###



def processor():
    """Stage 1: Function that takes the raw .zip file containing several JSON fiels and turns into a single, configurable JSON file"""

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

        print("Starting Stage 1: JSON processing")
        # user inform

        if Config.getboolean("DSI", "dsi_Export"):
            # if the config option for DSI is on, uses a pre-set list

            fields_to_remove = [
                "ip_addr", 
                "ip_addr_decrypted", 
                "audiobook_title", 
                "audiobook_uri", 
                "audiobook_chapter_uri", 
                "audiobook_chapter_title", 
                "offline_timestamp", 
                "conn_country",
                "reason_start",
                "reason_end",
                "shuffle",
                "skipped",
                "username",
                "platform",
                "username",
                "offline",
                "episode_name",
                "episode_show_name",
                "spotify_episode_uri",
                "user_agent_decrypted",
                "incognito_mode"
                ]
            # the list of fields DSI doesn't use at all

        else:
            # if the config option for DSI export isn't on

            fields_to_remove = [
                "ip_addr", 
                "ip_addr_decrypted", 
                "audiobook_title", 
                "audiobook_uri", 
                "audiobook_chapter_uri", 
                "audiobook_chapter_title", 
                "offline_timestamp", 
                "conn_country", 
                "username", 
                "episode_name", 
                "episode_show_name", 
                "spotify_episode_uri"
                "user_agent_decrypted"
                ]

            # the base list of information to filter out (there is borderline no reason to keep any of these - audiobooks are deprecated and only show up on extremely old data)

            if not Config.getboolean("Options", "track_URI_Enabled"):
                fields_to_remove.append("spotify_track_uri")

            if not Config.getboolean("Options", "time_Played_Enabled"):
                fields_to_remove.append("ms_played")

            if not Config.getboolean("Options", "timestamp_Enabled"):
                fields_to_remove.append("ts")

            if not Config.getboolean("Options", "start_Reason_Enabled"):
                fields_to_remove.append("reason_start")

            if not Config.getboolean("Options", "stop_Reason_Enabled"):
                fields_to_remove.append("reason_end")

            if not Config.getboolean("Options", "shuffle_Enabled"):
                fields_to_remove.append("shuffle")

            if not Config.getboolean("Options", "skip_Enabled"):
                fields_to_remove.append("skipped")

            if not Config.getboolean("Options", "platform_Enabled"):
                fields_to_remove.append("platform")

            if not Config.getboolean("Options", "offline_Enabled"):
                fields_to_remove.append("offline")

            if not Config.getboolean("Options", "incognito_Enabled"):
                fields_to_remove.append("incognito_mode")

        jsonLength = len(names)
        # counts how many files there are in the zip file

        progress = 1
        # sets a counter for progress to 1

        for name in jsonNames:
            # goes through json files one by one

            content = dataFiles.read(name)
            # reads the file
            parsedData = json.loads(content)
            # picks out the data from the read file

            progress += 1
            # adds 1 to counter every time a file is read
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

        print("Stage 1 complete!\n")
        # finishes work and checks if user wants to continue

        if Config.getboolean("DSI", "dsi_Export"):
            # if DSI is enabled in config
            print("DSI export enabled, proceeding to Stage 2")
            # user inform and immediate next task
            analyserStarter()

        else:
            continueToAnalyser = input("Do you wish to continue to Stage 2? Y/N: ")
            if continueToAnalyser == "y" or continueToAnalyser == "Y":
                analyserStarter()
            else:
                print("Exiting - feel free to close")
                time.sleep(60)
                raise SystemExit



### Stage 2: JSON -> Formatted CSV "Analyser" ###



def analyser(start, end, streamList, enableHeader=False):
    """Stage 2: Function that takes the processed json file and turns them into a formatted CSV file"""
    
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
        singleStreamPlatform = singleStream.get("platform")
        singleStreamURL = singleStream.get("spotify_track_uri")
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
            "Platform": [singleStreamPlatform],
            "URI": [singleStreamURL],
            "Offline": [singleStreamOffline],
            "Incognito": [singleStreamIncognito]
        }))
        
    pd.concat(csvList).to_csv("./Data/CSV/formatted.csv", mode='a', index=False, header=enableHeader)
    # pushes the list into the CSV (in append mode, since it gets cleared before call - this way it can be split in task)
    print(f"Processed CSV lines: {start:,.0f} - {(end - 1):,.0f}")
    # prints the completed point



### Pre-Stage 2: Analyser Starter Function ###



def analyserStarter():
    """Stage 2 Starter: Small function that calculates start/end points for Analyser and runs it if conditions are met"""

    if os.path.exists('./Data/CSV/formatted.csv'):
        # if the formatted.csv file already exists
        print("Starting Stage 2: JSON -> CSV\n")
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
            print(f"JSON split into 10 chunks, each chunk contains {streamListChunk:,.0f} lines\n")
            # splits the length into 10 equal (integer) chunks (/ = float, // = int) (helps with memory and user inform)

            for chunk in range(10):
                # for every CSV line-chunk between 0 and 9 (since CSV gets split into 10 parts)

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

            print("Stage 2 complete!\n")

            if Config.getboolean("DSI", "dsi_Export"):
                # if DSI is enabled in config
                print("DSI export enabled, proceeding to Stage 3")
                # user inform and immediate next task
                mathematician()

            else:
                continueToMathematician = input("Do you wish to continue to Stage 3? Y/N: ")
                if continueToMathematician == "y" or continueToMathematician == "Y":
                    mathematician()
                else:
                    print("Exiting - feel free to close")
                    time.sleep(60)
                    raise SystemExit



### Counter ###

def counter(fakeList):
    """Helper function that turns requested list into a pandas series to drop "nan" values, then turns back into a list"""
    return dict(Counter(list(pd.Series(fakeList).dropna())))
    # is called by mathematician to dynamically count the grouped data's aggregate values



### Stage 3: Mathematician (formatted.csv -> grouped.csv/dsi.csv) ###



def mathematician():
    """Stage 3: Function to turn the formatted CSV files into grouped, data-calculated CSVs"""

    print("Combining indices and calculating final numbers\n")

    csvData = pd.read_csv('./Data/CSV/formatted.csv')
    # opens the formatted.csv file as csvData

    if not Config.getboolean("DSI", "dsi_Export"):
        # if the config is set to save tracks, and DSI is not on
        csvData.set_index(["Track", "Artist", "Album"])
        # sets a multi-index to track, artist and album
        csvGrouped = csvData.groupby(["Track", "Artist", "Album"]).agg({"Duration": list, "Date": list, "Time": list, "Total Time": sum, "Start Reason": counter, "End Reason": counter, "Shuffle": counter, "Skipped": counter, "Platform": counter, "URI": counter, "Offline": counter, "Incognito": counter})
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

        print("Stage 3 complete!\n")
        # stage 3 end inform

        print("Stage 4 contains a chart-drawing function and a summary function. You can choose which one:")
        # stage 4 pre-prompt (choice between charter and summary)
        time.sleep(2)
        # quick wait 

        continueToSummary = input("Do you wish to continue to Stage 4 (Summary)? Y/N: ")
        if continueToSummary == "y" or continueToSummary == "Y":
            print("Summary function is currently not implemented, please check for an update")
            time.sleep(10)
            raise SystemExit
            #summary()
        else:
            continueToCharter = input("Do you wish to continue to Stage 4 (Charts)? Y/N: ")
            if continueToCharter == "y" or continueToCharter == "Y":
                print("Chart function currently not implemented, please check for an update")
                time.sleep(10)
                raise SystemExit
                #charter()
            else:
                print("Exiting - feel free to close")
                time.sleep(60)
                raise SystemExit
 
    
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
        # "explodes" the CSV (takes all the tracks with multiple URIs and splits them into their own rows with identical data across the track's URIs)
        csvDiscord.set_index("URI", inplace=True)
        # sets the index to URI
        csvDiscord.to_csv('./Data/CSV/dsi.csv', index=True)
        # pushes the whole modified dataframe into a CSV file, now with URI as index

        print("DSI Export successful! Exiting - feel free to close")
        # DSI export finished
        time.sleep(60)
        raise SystemExit
    




### Stage 4: Summary ##


def summary():
    """Stage 4-1 / Summary function"""

    if os.path.exists('./Data/CSV/grouped.csv'):
        # checks if there's a file to take summarized data from
        csvSum = pd.read_csv('./Data/CSV/grouped.csv')
        # 
        csvSum

    else:
        print("Stage 4 failed - no Stage 3 CSV found!")

        # this takes the grouped data and makes a quick summary (top 10/50 songs, total playtime, playtime per month?)
        # playtime per timeperiod requires something where it finds the year/month and then stores the list number, then takes all the playtime for those indices

# add summary function that lists the basic things:
#    - total playtime
#        pretty easy, just sum("playtime")
#    - most played songs (top 10, 50?)
#        bit more, will need to groupby again but just time?
#    - playtime per timeperiod (month, year)?
#        bunch more, will need to select the timeframe, then check the playtime for each song in that timeframe and sort by highest
#    - favorite artist/album
#        not that bad, just combine all the artist/album appearances and ignore songs, then take total playtime (so will also need the groupby time)

def charter():
    """Stage 4-2 / final function that draws charts from the finalised data"""
    print("unimplemented")








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



print(f"Starting Spotify (History) Analyser {SHAver}")
# start print

dataArray = os.listdir("./Data")
# stores the directory

zips = [zipP for zipP in dataArray if zipP.endswith("zip")]
# checks the directory for files with .zip, used to select the zip file

Config = configparser.ConfigParser(comment_prefixes=["#", "/"], allow_no_value=True)
Config.read('./config.ini')
# this opens the config file to be checked later

gui = easygui
# creates the file selection gui



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
    zipPath = gui.fileopenbox(title=("Please select your streaming history file"), filetypes=["*.zip"])
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

    if Config.getboolean("Function", "always_Skip_Stage_1"):
        # if the config setting for skipping Stage 1 is True, prompts to skip to analyser
        print("The config option to skip Stage 1 is enabled")
        
        if Config.getboolean("Function", "always_Skip_Stage_2"):
            # if both Stage 1 and 2 are set to skip, moves to Stage 3
            print("The config option to skip Stage 2 is enabled, starting Stage 3")
            mathematician()

        else:
            # if the config setting for skipping processor is on, but the analysation setting is off, starts analyser
            print("Skipping Stage 1, starting Stage 2")
            analyserStarter()

    else:
        # if the config setting to skip Stage 1 is False
        overwriteStatus = input('The Stage 1 data file already exists, do you want to overwrite it and re-do Stage 1? Y/N: ')
        # checks if the processed.json file already exists and checks config status, warns user if yes

        if overwriteStatus == "Y" or overwriteStatus == "y":
            # if the prompt is yes 
            print("Overwriting existing data, starting Stage 1\n")
            processor()
            # if user wants to ignore previous data and re-process or process new data, starts Stage 1

        else:
            # if user doesn't want to 
            skipStage1 = input('Do you want to skip Stage 1? Y/N: ')
            # user does not want to overwrite data, asking if skip processing altogether

            if skipStage1 == "Y" or skipStage1 == "y":

                if Config.getboolean("Function", "always_Skip_Stage_2"):
                    print("Stage 2 skip enabled in config, starting Stage 3")
                    mathematician()
                    # anaylser skip is enabled in config, automatically enters math phase

                else:
                    skipAnalyser = input('Do you want to skip Stage 2? Y/N:')
                    if skipAnalyser == "Y" or skipAnalyser == "y":
                        print("Skipping Stages 1 and 2, starting Stage 3")
                        mathematician()
                        # manual method to skip processing and analysing via input chain
                    else:
                        print("Analysing. \n")
                        analyserStarter()
                        # user wants to skip processing but wants to analyse existing data

            elif skipStage1 == "N" or skipStage1 == "n":

                raise SystemExit
                # wants to not overwrite data, but doesn't want to skip processing either, exit

elif not os.path.exists('./Data/processed.json'):
    # in case the file does not exist

    if Config.getboolean("DSI", "dsi_Export"):
        # in case the file does not exist, and DSI is enabled
        print("No processed file found and DSI exporting is enabled, processing data to fit DSI requirements")
        processor()

    else:
        print("No processed file found, starting program from Stage 1")
        processor()

else:
    print("Unknown error occurred, please check files and try again")
    raise SystemExit
    # shouldn't ever happen, but exits the program rather than erroring out