import zipfile
import os
import json



###################
# CUSTOMISATION
# these are all the different types of information that Spotify stores, turn them on/off at your leisure
# audiobooks are ignored, songs and episodes can be turned on/off
#
timeStampEnabled = True
# timestamp (when the track was started)
usernameEnabled = False
# username (username)
platformEnabled = False
# platform (Android, Chromecast, iOS, etc)
timePlayedEnabled = True
# time listened to each track (this is the main thing people want, recommended to keep on)
countryEnabled = False
# list country per track (location that Spotify logged)
userAgentEnabled = False
# list the streaming agent (Safari, Firefox, etc)
trackNameEnabled = True
# name of the track 
artistNameEnabled = True
# name of the artist
albumNameEnabled = True
# name of the album
trackURLEnabled = False
# Spotify's own URL for the track
startReasonEnabled = True
# why the track was started
stopReasonEnabled = True
# why the track stopped
shuffleEnabled = True
# if Shuffle was enabled during the track
skipEnabled = True
# if the track was skipped prematurely
offlineEnabled = False
# if the user was offline during the track
incognitoEnabled = False
# if the user was in a private session.
episodesEnabled = False
# whether to track episode info (also enables show name). 
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
                if timeStampEnabled == False:
                    stream.pop("ts", None)
                if usernameEnabled == False:
                    stream.pop("username", None)
                if platformEnabled == False:
                    stream.pop("platform", None)
                if timePlayedEnabled == False:
                    stream.pop("ms_played", None)
                if countryEnabled == False:
                    stream.pop("conn_country", None)
                if userAgentEnabled == False:
                    stream.pop("user_agent_decrypted", None)
                if trackNameEnabled == False:
                    stream.pop("master_metadata_track_name", None)
                if artistNameEnabled == False:
                    stream.pop("master_metadata_album_artist_name", None)
                if albumNameEnabled == False:
                    stream.pop("master_metadata_album_album_name", None)
                if trackURLEnabled == False:
                    stream.pop("spotify_track_uri", None)
                if startReasonEnabled == False:
                    stream.pop("reason_start", None)
                if stopReasonEnabled == False:
                    stream.pop("reason_end", None)
                if shuffleEnabled == False:
                    stream.pop("shuffle", None)
                if skipEnabled == False:
                    stream.pop("skipped", None)
                if offlineEnabled == False:
                    stream.pop("offline", None)
                if incognitoEnabled == False:
                    stream.pop("incognito_mode", None)
                if episodesEnabled == False:
                    stream.pop("episode_name", None)
                    stream.pop("episode_show_name", None)
                else:
                    None
                # removes all the unwanted information according to the each of the True/False statements at the document start
                output.append(stream)
            with open('./Data/processed.json', 'w') as a2:
                json.dump(output, a2, ensure_ascii=True, indent=0)
                # takes all the streams in 'output' and dumps them into the 'processed.json' files
    print("Processing complete, beginning analysing")
    output.clear()
    # empties the massive list of data
    analyser()
    # calls the analyser to start the next step

def analyser():
    with open('./Data/processed.json', 'r') as processedStreams:
        a3 = processedStreams.read()
        streamList = json.loads(a3)
        # starts the analysation by reloading the json in a different variable
        streamListLength = int((len(streamList)/50))
        # stores 1/50th of the length of the full list in a variable so it can be processed in 2% chunks
        for a4 in range(0,50):
            print((streamListLength*a4), (streamListLength*(a4+1)))
            # this "works" in the sense that it does split it into 15,306 song chunks, but it cuts off the very end (765300 vs 765336) because of float -> int rounding
            # print(streamList[(streamListLength*(a4)):(streamListLength*(a4+1)) ])

        # fun fact len(a4) for me is 765,336, that's how many songs are in my streaming history - streamListLength/50 = ~15306 songs



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
# the directory information

if not dataArray:
    input("Please move your 'my_spotify_data.zip' file to the Data folder.\n")
    # has no files, needs user to move zip there
if 'mySpotifyData.zip' in dataArray:
    fileName = "mySpotifyData.zip"
    print("Correct file found\n")
    # the first file in the directory is the correct zip file
if len(dataArray) < 3:
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
else:
    print("Too many files found in the Data folder, please remove unnecessary files.\n")
    raise SystemExit
    # the correct file wasn't found and too may files are present

path = "./Data/" + fileName
# combines the folder path to make the final path leading to the right file



if os.path.exists('./Data/processed.json') == True:
    ovwr = input('The data file already exists, do you want to overwrite it? Y/N: ')
    if ovwr == "Y" or "y":
        print("\n")
        processor()
    elif ovwr == "N" or "n":
        print("\n")
        skipProcessor = input('Do you want to skip the processing and begin analysation? Y/N: ')
        if skipProcessor == "Y" or "y":
            print("\n")
            analyser()
        elif skipProcessor == "N" or "n":
            raise SystemExit
    else: 
        print("Unknown command, try again. \n")
        raise SystemExit
else:
    None
# checks if the processed.json file already exists, warns user if yes






# next to-do:
# take the now filtered results from processed.json and turn them into full information
# ex. take all the streams from 2019 and add up the ms_played
# another thing is to find a way to do "unique:" (counter) and then sort the streams into number of x (times listened to, artist appearance, album...)
# next is time per action (per artist, per album)
# then to chart it all in some pretty way