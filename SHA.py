import zipfile, os, json, datetime, configparser, time, ast
import numpy as np
import pandas as pd
import easygui
import tkinter as tk
from collections import Counter


SHAver = "v0.3.10.0016"



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

        if os.path.exists("./Data/stage1.json"):
            # checks if the processed file exists yet
            jsonEmptier = open("./Data/stage1.json", "w")
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

        with open("./Data/stage1.json", "w") as jsonDone:
            # opens the processed file in write mode
            json.dump(output, jsonDone, ensure_ascii=True, indent=0)
                # takes all the streams in 'output' and dumps them into the 'stage1.json' file

        print("Stage 1 complete!\n")
        # finishes work and checks if user wants to continue

        if Config.getboolean("DSI", "dsi_Export"):
            # if DSI is enabled in config
            print("DSI export enabled, proceeding to Stage 2")
            # user inform and immediate next task
            StageTwoStarter()

        else:
            continueToStage2 = input("Do you wish to continue to Stage 2? Y/N: ")
            if continueToStage2 == "y" or continueToStage2 == "Y":
                StageTwoStarter()
            else:
                print("Exiting - feel free to close")
                time.sleep(60)
                raise SystemExit



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
        singleStreamPlaytime = singleStream.get("ms_played")
        singleStreamTimestamp = singleStream.get("ts")
        singleStreamTemp = datetime.datetime.fromisoformat(singleStreamTimestamp)
        singleStreamDate = singleStreamTemp.strftime("%Y-%m-%d")
        singleStreamTime = singleStreamTemp.strftime("%H:%M:%S")
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
        
    pd.concat(csvList).to_csv("./Data/CSV/stage2.csv", mode="a", index=False, header=enableHeader)
    # pushes the list into the CSV (in append mode, since it gets cleared before call - this way it can be split in task)
    print(f"Processed lines: {start:,.0f} - {(end - 1):,.0f}")
    # prints the completed point



### Pre-Stage 2: Analyser Starter Function ###



def StageTwoStarter():
    """Stage 2 Starter: Small function that calculates start/end points for Analyser and runs it if conditions are met"""

    print("Starting Stage 2: JSON -> CSV\n")
    # user inform

    if os.path.exists("./Data/CSV/stage2.csv"):
        # if the stage2.csv file already exists
        
        csvEmptier = open("./Data/CSV/stage2.csv", "w")
        csvEmptier.truncate()
        csvEmptier.close()
        # opens the csv, writes nothing (effectively deleting everything), then closes the file

    with open("./Data/stage1.json", "r") as processedStreams:
        # opens the stage1.json file
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

        if Config.getboolean("DSI", "dsi_Export"):
            # if DSI is enabled in config
            print("DSI export enabled, proceeding to Stage 3")
            # user inform and immediate next task
            StageThree()

        else:
            continueToStage3 = input("Do you wish to continue to Stage 3? Y/N: ")
            if continueToStage3 == "y" or continueToStage3 == "Y":
                StageThree()
            else:
                print("Exiting - feel free to close")
                time.sleep(60)
                raise SystemExit



### Stage 3: Mathematician (stage2.csv -> stage3.csv/dsi.csv) ###



# Counter #

def counter(fakeList):
    """Helper function that turns requested list into a pandas series, drops "nan" (unavailable) values, then turns back into a list"""
    return dict(Counter(list(pd.Series(fakeList).dropna())))
    # is called to dynamically count the grouped data's aggregate values (time, reasons, booleans, etc)

# Main #

def StageThree():
    """Stage 3: Function to turn the formatted CSV files into grouped, data-calculated CSVs"""

    print("Starting Stage 3: CSV cleanup\n")
    # user inform

    csvData = pd.read_csv("./Data/CSV/stage2.csv")
    # opens the stage2.csv file as csvData

    if not Config.getboolean("DSI", "dsi_Export"):
        # if DSI exporting isn't true, uses the "main" method of grouping
        csvData.set_index(["Track", "Artist", "Album"])
        # sets a multi-index to track, artist and album
        csvGrouped = csvData.groupby(["Track", "Artist", "Album"]).agg({"Duration": list, "Date": list, "Time": list, "Total Time": sum, "Start Reason": counter, "End Reason": counter, "Shuffle": counter, "Skipped": counter, "Platform": counter, "URI": counter, "Offline": counter, "Incognito": counter})
        # combines all occurances of a track that has the same name, artist and album into one multi-index - creates a dictionary for most pieces of info, except duration, which it sums up (as milliseconds)
        print("CSV data grouped, calculating playcounts")
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
        csvGrouped.to_csv("./Data/CSV/stage3.csv", index=True)
        # pushes the whole modified dataframe into a csv file

        print("Stage 3 complete!\n")
        # stage 3 end inform

        continueToStage4 = input("Do you wish to continue to Stage 4? Y/N: ")
        if continueToStage4 == "y" or continueToStage4 == "Y":
            opSelStage4()
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
    


### Stage 4: Summary ###



def StageFourSummary():
    """Stage 4-1 / Summary function"""

    csvSum = pd.read_csv("./Data/CSV/stage3.csv")
    # opens the finalised CSV file

    topTracks = int(Config.get("Summary", "number_Of_Tracks"))
    # checks the config for how many songs to get the top status for, ensures it's integer

    topType = Config.get("Summary", "top_Type")
    # stores the config setting for the type of data to sort top by (time vs count)

    if topTracks < 3:
        topTracks = 3
        # ensures the top list has at least 3 tracks
    if topTracks > 50:
        topTracks = 50
        # ensures it has no more than 50 tracks (top list, not all list)

    print(f"Selected top {topTracks} tracks, creating a summary\n")
    # quick user update

    topAlbums = int(Config.get("Summary", "top_Albums"))
    # stores the config setting for the number of albums to get

    topArtists = int(Config.get("Summary", "top_Artists"))
    # stores the config setting for the number of albums to get

    ttSummaryTopText = Config.get("Summary", "top_Text")
    # saves the top text from config

    if topType == "Time" or topType == "time":
        # if the config setting is set to get the top by Time played
        ttCSVraw = csvSum.nlargest(topTracks, ["Total Time"])
    else:
        # if the config setting is set to get the top by number of times played
        ttCSVraw = csvSum.nlargest(topTracks, ["Playcount"])
        # grabs the 10 most playcount songs from CSV by the playcount

    ttCSVclean = ttCSVraw.get(["Track", "Playcount", "Total Time", "Album", "Artist", "Date", "Time", "Duration"])
    # only grabs the relevant details about the top songs

    ttCSVclean.reset_index(inplace=True)
    # resets the index and makes it "in place" (modifies the dataframe, doesn't make a new one)


    ### Top Tracks ### 

    num = 0
    ttPlaycount = ""
    # sets up temp variables for string constructors

    ttCSVplaycount = ttCSVclean["Playcount"]
    ttCSVtotaltime = ttCSVclean["Total Time"]
    ttCSVartist = ttCSVclean["Artist"]
    # sets up temp variables to call for dataFrame

    if topTracks == 1:
        trackPrefix = "Favorite track"
    elif topTracks == 0:
        trackPrefix = ""
    else:
        trackPrefix = "Favorite tracks"    
    
    if topType == "Time" or topType == "time":
        # if the config calls for playtime
        for song in ttCSVclean["Track"]:
            # repeats for every track in the top list

            string = f"#{num+1}: {song} by {ttCSVartist.get(num)}\n     Played for {ttCSVtotaltime.get(num)/60000:,.1f} minutes\n       Played {ttCSVplaycount.get(num):,.0f} times\n"
            # creates a formatted string with each track
            ttPlaycount = f"{ttPlaycount}\n{string}"
            # joins together the track strings and makes them new lines
            num += 1
            # adds 1 to the number (ranking)

    else:
        # if the config calls for playcount
        for song in ttCSVclean["Track"]:
            # repeats for every track in the top list

            string = f"#{num+1}: {song} by {ttCSVartist.get(num)}\n     Played {ttCSVplaycount.get(num):,.0f} times\n       Played for {ttCSVtotaltime.get(num)/60000:,.1f} minutes\n"
            # creates a formatted string with each track
            ttPlaycount = f"{ttPlaycount}\n{string}"
            # joins together the track strings and makes them new lines
            num += 1
            # adds 1 to the number (ranking)


    ttTotalTime = (f"{(csvSum["Total Time"].sum() / 1000 / 60)/ 60:,.2f} hours or {(csvSum["Total Time"].sum() / 1000 / 60):,.0f} minutes")
    # saves the total hours and minutes the CSV has (2- and 0-digit rounding)


    if Config.get("Options", "timestamp_Enabled"):
        # requires the timestamps to be enabled
        None
        # step 1: grab the *very earliest* timestamp there is (date)
        # step 2: use that earliest timestamp as the start
        # step 3: with a month's granularity, take every date that's included in that "grain" (if it's May 2022, it should store a list of every song's count of dates in that timeframe + playtime, every other data is irrelevant)
        # step 4: summarize the data (count per month in a separate dataframe?)
        # step 5: compare the data (May vs June vs August...) based on time vs count if (high-level)

    else:
        # if timestamps aren't available
        print("Timestamps aren't enabled in config, no time period data available")

    
    ### Top Artists ###

    if topArtists >= 1:
        # ensures there's at least one artist to check the top list for

        csvArtists = csvSum.get(["Artist", "Total Time", "Playcount"])
        # grabs only the relevant details
        csvArtists = csvArtists.groupby("Artist").agg({"Total Time": sum, "Playcount": sum})
        # groups the dataframe csvArtists by artists, counts up the total time

        ttArtists = csvArtists.nlargest(topArtists, ["Total Time"])
        # gets the config-determined number of top artists
        ttArtists.reset_index(inplace=True)
        # resets the index, so that the columns can be called by their index

        ttArtistsTime = ttArtists["Total Time"]
        ttArtistsCount = ttArtists["Playcount"]
        # sets up temp variables to call for dataFrame

        num = 0
        ttArtistString = ""
        # sets up temp variables for string constructors

        if topArtists == 1:
            artistPrefix = "Favorite Artist"
        elif topArtists == 0:
            artistPrefix = ""
        else:
            artistPrefix = "Favorite Artists"

        if topType == "Time" or topType == "time":
        # if the config calls for playtime
            for artist in ttArtists["Artist"]:
                # repeats for every artist in the top list

                string = f"#{num+1}: {artist}\n     Played for {ttArtistsTime.get(num)/60000:,.1f} minutes\n       Played {ttArtistsCount.get(num):,.0f} times\n"
                # creates a formatted string with each track
                ttArtistString = f"{ttArtistString}\n{string}"
                # joins together the track strings and makes them new lines
                num += 1
                # adds 1 to the number (ranking)

        else:
        # if the config calls for playcount
            for artist in ttArtists["Artist"]:
                # repeats for every artist in the top list

                string = f"#{num+1}: {artist}\n     Played {ttArtistsCount.get(num):,.0f} times\n       Played for {ttArtistsTime.get(num)/60000:,.1f} minutes\n"
                # creates a formatted string with each track
                ttArtistString = f"{ttArtistString}\n{string}"
                # joins together the track strings and makes them new lines
                num += 1
                # adds 1 to the number (ranking)


    ### Top Albums ###

    if topAlbums >= 1:
        # ensures there's at least one album to check the top list for

        csvAlbums = csvSum.get(["Album", "Total Time", "Playcount"])
        # grabs only the relevant details
        csvAlbums = csvAlbums.groupby("Album").agg({"Total Time": sum, "Playcount": sum})
        # groups the dataframe csvAlbums by albums, counts up the total time

        ttAlbums = csvAlbums.nlargest(topAlbums, ["Total Time"])
        # gets the config-determined number of top albums
        ttAlbums.reset_index(inplace=True)
        # resets the index, so that the columns can be called by their index

        ttAlbumsTime = ttAlbums["Total Time"]
        ttAlbumsCount = ttAlbums["Playcount"]
        # sets up temp variables to call for dataFrame

        num = 0
        ttAlbumString = ""
        # sets up temp variables for string constructors

        if topAlbums == 1:
            albumPrefix = "Favorite Album"
        elif topAlbums == 0:
            albumPrefix = ""
        else:
            albumPrefix = "Favorite Albums"

        if topType == "Time" or topType == "time":
        # if the config calls for playtime
            for album in ttAlbums["Album"]:
                # repeats for every album in the top list

                string = f"#{num+1}: {album}\n     Played for {ttAlbumsTime.get(num)/60000:,.1f} minutes\n       Played {ttAlbumsCount.get(num):,.0f} times\n"
                # creates a formatted string with each album
                ttAlbumString = f"{ttAlbumString}\n{string}"
                # joins together the album strings and makes them new lines
                num += 1
                # adds 1 to the number (ranking)

        else:
        # if the config calls for playcount
            for album in ttAlbums["Album"]:
                # repeats for every album in the top list

                string = f"#{num+1}: {album}\n     Played {ttAlbumsCount.get(num):,.0f} times\n       Played for {ttAlbumsTime.get(num)/60000:,.1f} minutes\n"
                # creates a formatted string with each track
                ttAlbumString = f"{ttAlbumString}\n{string}"
                # joins together the album strings and makes them new lines
                num += 1
                # adds 1 to the number (ranking)   

    csvYM = csvSum
    # creates a separate dataframe form the existing csvSum (just because csvYM (Year Month) gets tweaked a lot)

    csvYM["Date"] = csvYM["Date"].apply(ast.literal_eval)
    # turns the column of dates in string format into lists

    csvYM["Duration"] = csvYM["Duration"].apply(ast.literal_eval)
    # turns the column of durations in string format into lists

    allDates = [date for sublist in csvYM["Date"] for date in sublist]
    # turns the individual lists per cell into a list of all the dates

    csvYM = csvYM.explode(["Date", "Duration"])
    # turns into a list of songs "exploded" by the dates and durations

    csvYM["Date"] = pd.to_datetime(csvYM["Date"])
    # ensures the dataframe now uses actual datetime format for the "date" column

    csvYM["Duration"] = pd.to_numeric(csvYM["Duration"])
    # ensures the dataframe now uses numbers for durations (shouldn't lead to "object" type errors)

    earliestDate = min(allDates)
    # gets the "lowest" (earliest) date from the megalist of dates

    latestDate = max(allDates)
    # gets the "highest" (latest) date from the megalist of dates

    print(f"Track dates range from {earliestDate} to {latestDate}")
    # user inform

    ### Top Months ###

    topMonthCount = int(Config.get("Summary", "top_Months"))
    # saves the config option for number of top months to get

    if topMonthCount == 1:
        monthPrefix = "Most listened to month"
    elif topMonthCount == 0:
        monthPrefix = ""
    else:
        monthPrefix = "Most listened to months"

    if topMonthCount >= 1:
        # ensures there's at least one month to check the top list for

        numberFormat = Config.get("Summary", "top_Month_Numbers").lower()
        # the config option for what the numbers should be formatted by (hours or minutes)

        topMonthType = Config.get("Summary", "top_Month_Type").lower()
        # the config option for how to sort months - each or total, each = every month is its own thing even across years, total = that month across all years

        if topMonthType == "each":
            # if the config option is on "each" (counts each month of each year as its own entity)

            monthDurations = csvYM.resample("MS", on="Date")["Duration"].sum()
            # adds up all the song durations based on the date they were listened to

            topMonths = monthDurations.nlargest(topMonthCount)
            # finds the config-based number of largest (most listened to) months, turns into a series

            num = 0
            ttTopMonth = ""
            # sets up temp variables

            for month, duration in topMonths.items():
                # repeats for every month in the top list

                if numberFormat == "minutes":
                    string = f"#{num+1}: {month.strftime("%B %Y")}\n     Listened for {duration/60000:,.1f} minutes\n"
                else:
                    string = f"#{num+1}: {month.strftime("%B %Y")}\n     Listened for {duration/360000:,.1f} hours\n"
                    # creates a formatted string with each month in the top list based on config

                ttTopMonth = f"{ttTopMonth}\n{string}"
                # joins together the month strings and makes them new lines
                num += 1
                # adds 1 to the number (ranking)

        if topMonthType == "total":
            # if the config option is on "total" (counts all months together)

            totalMonthDurations = csvYM.groupby(csvYM["Date"].dt.month)["Duration"].sum()
            # groups by the months, calculates the total duration for each month
            totalMonthDurations.index = pd.to_datetime(totalMonthDurations.index, format="%m").month_name()
            # formats the months into their names, keeping the order

            num = 0
            ttTopMonth = ""
            # sets up temp variables
            
            totalTopMonths = totalMonthDurations.nlargest(topMonthCount)
            # finds the config-based number of largest (most listened to) months, turns into a series

            for month, duration in totalTopMonths.items():
                # repeats for every month in the top list

                if numberFormat == "minutes":
                    string = f"#{num+1}: {month}\n     Listened for {duration/60000:,.1f} minutes\n"
                else:
                    string = f"#{num+1}: {month}\n     Listened for {duration/360000:,.1f} hours\n"
                    # creates a formatted string with each month in the top list

                ttTopMonth = f"{ttTopMonth}\n{string}"
                # joins together the month strings and makes them new lines
                num += 1
                # adds 1 to the number (ranking)

    else:
        # if the config option isn't set or is <1 
        ttTopMonth = ""


    ### Top Years ###

    topYearCount = int(Config.get("Summary", "top_Years"))
    # saves the config option for number of top years to get

    if topYearCount == 1:
        yearPrefix = "Most listened to year"
    elif topYearCount == 0:
        yearPrefix = ""
    else:
        yearPrefix = "Most listened to years"

    if topYearCount >= 1:
        # ensures there's at least one year to check the top list for

        yearDurations = csvYM.resample("YS", on="Date")["Duration"].sum()
        # adds up all the song durations based on the date they were listened to

        topYears = yearDurations.nlargest(topYearCount)
        # finds the config-based number of largest (most listened to) years, turns into a series

        ttTopYear = ""
        num = 0
        # sets up temp variables

        for year, duration in topYears.items():
            # repeats for every year in the top list
            string = f"#{num+1}: {year.strftime("%Y")}\n     Listened for {duration/360000:,.1f} hours\n"

            ttTopYear = f"{ttTopYear}\n{string}"
            # joins together the year strings and makes them new lines
            num += 1
            # adds 1 to the number (ranking)
    else:
        # if the config option isn't set or is <1
        ttTopYear = ""


    ### Summary Writer ###

    topTracks = (
                f"{ttSummaryTopText}\n\n\n"
                "\n"
                f"{artistPrefix}:\n{ttArtistString}\n\n"
                "\n"
                f"{albumPrefix}:\n{ttAlbumString}\n\n"
                "\n"
                f"{trackPrefix}:\n{ttPlaycount}\n\n"
                "\n"
                f"Total time spent listening:\n\n{ttTotalTime}\n\n\n"
                "\n"
                f"{monthPrefix}:\n{ttTopMonth}\n\n"
                "\n"
                f"{yearPrefix}:\n{ttTopYear}"
                )
    # stores all the information as formatted strings printed across newlines
    
    with open("./Data/summary.txt", "w", encoding="utf-8") as tts:
        # opens hours.txt
        tts.write(topTracks)
        # pushes the hours text to the file

    tts.close()
    # closes the text file

    print("Stage 4 - Summary finished!\n")
    # user inform

    print("Exiting - feel free to close")
    #time.sleep(600)
    raise SystemExit
    # exit because no task left



### Stage 4: Charting ###



def StageFourCharter():
    """Stage 4-2 / Charting function"""
    print("unimplemented")
    # still requires a ton of stuff, mainly a charter plugin, maybe prompt whether the data should be displayed or just saved (will save with display)



### Setup ###



print(f"Starting Spotify (History) Analyser {SHAver}\n")
# start print

dataArray = os.listdir("./Data")
# stores the directory

zips = [zipP for zipP in dataArray if zipP.endswith("zip")]
# checks the directory for files with .zip, used to select the zip file

Config = configparser.ConfigParser(comment_prefixes=["#", "/"], allow_no_value=True)
Config.read("./config.ini")
# this opens the config file to be checked later

gui = easygui
# creates the file selection gui in case it's needed



# Zip file selector
if "mySpotifyData.zip" in dataArray:
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



### User Operation Selector ###



def opSelStage1():
    """Function that checks if Stage 1 should be performed"""

    if Config.getboolean("Function", "always_Skip_Stage_1"):
        # the config option to skip Stage 1 is enabled
        print("The config option to skip Stage 1 is enabled")
        opSelStage2()
        # calls Stage 2 user opSel
    else:
        RedoStage1 = input("The Stage 1 data file already exists, do you want to overwrite it and re-do Stage 1? Y/N: ")
        # asks if user wants to start at Stage 1 regardless of data file status

        if RedoStage1 == "Y" or RedoStage1 == "y":
            # if yes, starts at Stage 1
            StageOne()
            # starts Stage 1 function

        else:
            print("Skipped Stage 1")
            opSelStage2()
            # calls Stage 2 user opSel



def opSelStage2():
    """Function that checks if Stage 2 should be performed"""

    if Config.getboolean("Function", "always_Skip_Stage_2"):
        # the config option to skip Stage 2 is enabled
        print("The config option to skip Stage 2 is enabled")
        opSelStage3()
        # calls Stage 3 user opSel
    else:
        StartStage2 = input("Do you want to start Stage 2? Y/N: ")
        # asks if user wants to start at Stage 1 regardless of data file status

        if StartStage2 == "Y" or StartStage2 == "y":
            # if yes, starts at Stage 2
            StageTwoStarter()
            # starts Stage 2 function (starter)

        else:
            print("Skipped Stage 2")
            opSelStage3()
            # calls Stage 3 user opSel



def opSelStage3():
    """Function that checks if Stage 3 should be performed"""

    if Config.getboolean("Function", "always_Skip_Stage_3"):
        # the config option to skip Stage 3 is enabled
        print("The config option to skip Stage 3 is enabled")
        opSelStage4()
        # calls Stage 3 user opSel
    else:
        StartStage3 = input("Do you want to start Stage 3? Y/N: ")
        # asks if user wants to start at Stage 1 regardless of data file status

        if StartStage3 == "Y" or StartStage3 == "y":
            # if yes, starts at Stage 3
            StageThree()
            # starts Stage 3 function

        else:
            print("Skipped Stage 3")
            opSelStage4()
            # calls Stage 4 user opSel



def opSelStage4():
    """Function to pick which Stage 4 task to perform (Summary vs Charter)"""

    if os.path.exists("./Data/CSV/stage3.csv"):
        # checks if the CSV exists
        Stage4Selection = input("There are two possible ways to display data - a (S)ummary of data or (C)harts.\nPlease select - S/C: ")
        # asks which Stage 4 operation to perform (Summary is standalone, Charts requires Summary file)

        if Stage4Selection == "C" or Stage4Selection == "c":
            # if the selected Stage 4 op is (C)harter
            if os.path.exists("./Data/topTracks.txt"):
                print("Starting Stage 4 - Charts\n")
                StageFourCharter()
            else:
                print("Charts require a Summary file - creating one")
                # charts require a summary txt to exist
                StageFourSummary()

        else:
            # if the selected Stage 4 op is (S)ummary
            print("Starting Stage 4 - Summary\n")
            StageFourSummary()
        
    else:
        # if the CSV doesn't exist
        print("There is no Stage 3 CSV to read.\nPlease ensure the program finishes Stage 3 at least once.")
        print("Exiting - feel free to close")
        time.sleep(600)
        raise SystemExit



### Task Starting Logic ###


if os.path.exists("./Data/stage1.json"):
    # if the processed file exists (meaning this program has been run at least once)
    print("You'll be prompted to choose processing stages. Stages 1-3 are for processing data, 4 is for displaying existing data")
    print('Declining a Stage will prompt you about the next stage - enter "N" to decline, "Y" to accept. Press Ctrl+C or Alt+F4 or close the app to quit\n')
    # prints quick user inform

    opSelStage1()
    # calls the first stage user operation selector

elif not os.path.exists("./Data/stage1.json"):
    # in case the file does not exist

    if Config.getboolean("DSI", "dsi_Export"):
        # in case the file does not exist, and DSI is enabled
        print("No processed file found and DSI exporting is enabled, processing data to fit DSI requirements")
        StageOne()

    else:
        print("No processed file found, starting program from Stage 1")
        StageOne()

else:
    print("Unknown error occurred, please check files and try again")
    raise SystemExit
    # shouldn't ever happen, but exits the program rather than erroring out