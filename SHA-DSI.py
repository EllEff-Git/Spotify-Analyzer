import zipfile, os, json, time
import numpy as np
import pandas as pd
import easygui
import tkinter as tk


SHA_DSIver = "v0.3.18.1628"



### Stage 1: Raw JSON Processor ###



def StageOne():
    """Stage 1: Function that takes the raw .zip file containing several JSON fiels and turns into a single, configurable JSON file"""

    with zipfile.ZipFile(zipPath, "r") as dataFiles:
        # opens the zip file via pre-determined path

        names = dataFiles.namelist()
        # takes each json file individually
        jsonNames = [a1 for a1 in names if a1.endswith("json")]
        # excludes all the files that don't end in .json
        jsonNames.sort()
        # poorly sorts the files (since it goes alphabetically, - comes before _, so e.g 2019-2020 is processed before 2019_)

        output = []
        # creates a progress counter and a list for the outputs to go

        if os.path.exists("./Data/DSIstage1.json"):
            # checks if the processed file exists yet
            jsonEmptier = open("./Data/DSIstage1.json", "w")
            jsonEmptier.truncate()
            jsonEmptier.close()
            # opens, adds "nothing" and closes the processed file

        print("Starting Stage 1: JSON processing")
        # user inform

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

        with open("./Data/DSIstage1.json", "w") as jsonDone:
            # opens the processed file in write mode
            json.dump(output, jsonDone, ensure_ascii=True, indent=0)
                # takes all the streams in 'output' and dumps them into the 'stage1.json' file

        print("Stage 1 complete!\n")
        # finishes work, starts Stage 2

        StageTwoStarter()



### Stage 2: JSON -> Formatted CSV "Analyser" ###



def StageTwo(start, end, streamList, enableHeader=False):
    """Stage 2: Function that takes the processed json file and turns them into a formatted CSV file"""
    
    csvList = []
    # makes an empty list to store items in
   
    for stream in range(start, end):
        # for every stream in the set range (by chunk)
        singleStream = streamList[stream]
        # each stream is one from the list
        singleStreamName = singleStream.get("master_metadata_track_name")
        singleStreamArtist = singleStream.get("master_metadata_album_artist_name")
        singleStreamAlbum = singleStream.get("master_metadata_album_album_name")
        singleStreamPlaytime = singleStream.get("ms_played")
        singleStreamURL = singleStream.get("spotify_track_uri")
        # grabs all the different information types the CSV has
        
        csvList.append(pd.DataFrame({
            "Track": [singleStreamName],
            "Artist": [singleStreamArtist],
            "Album": [singleStreamAlbum],
            "Duration": [singleStreamPlaytime],
            "Total Time": [singleStreamPlaytime],
            "URI": [singleStreamURL],
        }))
        
    pd.concat(csvList).to_csv("./Data/CSV/DSIstage2.csv", mode="a", index=False, header=enableHeader)
    # pushes the list into the CSV (in append mode, since it gets cleared before call - this way it can be split in task)
    print(f"Processed lines: {start:,.0f} - {(end - 1):,.0f}")
    # prints the completed point



### Pre-Stage 2: Analyser Starter Function ###



def StageTwoStarter():
    """Stage 2 Starter: Small function that calculates start/end points for Analyser and runs it if conditions are met"""

    print("Starting Stage 2: JSON -> CSV\n")
    # user inform

    if os.path.exists("./Data/CSV/DSIstage2.csv"):
        # if the DSIstage2.csv file already exists
        
        csvEmptier = open("./Data/CSV/DSIstage2.csv", "w")
        csvEmptier.truncate()
        csvEmptier.close()
        # opens the csv, writes nothing (effectively deleting everything), then closes the file

    with open("./Data/DSIstage1.json", "r") as processedStreams:
        # opens the DSIstage1.json file
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

            StageTwo(startPoint, endPoint, streamList, enableHeader)
            # passes the start and end points, as well as the list to process 
    
            print(f"Progress: {(chunk + 1) * 10}%")
            # prints the progress (every 10%, since there's 10 chunks)

        print("Stage 2 complete!\n")

        StageThree()



### Stage 3: Mathematician (DSIstage2.csv -> dsi.csv) ###



def StageThree():
    """Stage 3: Function to turn the formatted CSV files into grouped, data-calculated CSVs"""

    print("Starting Stage 3: CSV cleanup\n")
    # user inform

    csvData = pd.read_csv("./Data/CSV/DSIstage2.csv")
    # opens the DSIstage2.csv file as csvData

    csvData.set_index("Track", inplace=True)
    # sets the CSV index to "track"
    csvDiscord = csvData.groupby(["Track"]).agg({"Artist": "first", "Album": "first", "Duration": list, "Total Time": sum, "URI": lambda x: list(set(x))})
    # stores the csvData as a groupby of just the track (this is what DSI requires to function)

    csvDiscord["Playcount"] = csvDiscord["Duration"].apply(len)
    # calculates the length of "Duration" list per column and saves it as "Playcount" column
    columns = ["Playcount"] + [col for col in csvDiscord.columns if col != "Playcount"]
    # automatically moves the "Playcount" column to the first position
    csvDiscord = csvDiscord[columns]
    # after all tracks are done and the for loop ends, inserts a new column containing the playcount for each track

    csvSeconds = (csvDiscord["Total Time"].sum() / 1000)
    # takes the total hours from the csv (turns total time for each track from milliseconds to (/1000) seconds to minutes (/60) to hours (/60)
    csvMinutes = (csvSeconds / 60)
    # turns the second variable to minutes
    csvHours = (csvMinutes / 60)
    # turns the minute variable to hours

    csvTimes = (
        f"Total hours = {csvHours}\n"
        f"Total minutes = {csvMinutes}\n"
        f"Total seconds = {csvSeconds}"
    )

    with open("./Data/CSV/totalTimes.txt", "w") as times:
        # opens hours.txt
        times.write(csvTimes)
        # pushes the times text to the file
    times.close()
    # closes the file

    csvDiscord = csvDiscord.explode("URI")
    # "explodes" the CSV (takes all the tracks with multiple URIs and splits them into their own rows with identical data across the track's URIs)
    csvDiscord.set_index("URI", inplace=True)
    # sets the index to URI
    csvDiscord.to_csv("./Data/CSV/dsi.csv", index=True)
    # pushes the whole modified dataframe into a CSV file, now with URI as index

    print("DSI Export successful! Exiting - feel free to close")
    # DSI export finished
    time.sleep(60)
    raise SystemExit



### Setup ###



print(f"Starting Spotify (History) Analyser - DSI Variant - {SHA_DSIver}")
# start print

dataArray = os.listdir("./Data")
# stores the directory

zips = [zipP for zipP in dataArray if zipP.endswith("zip")]
# checks the directory for files with .zip, used to select the zip file

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



StageOne()
# starts the program from stage 1