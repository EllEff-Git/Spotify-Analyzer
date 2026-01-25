import zipfile
import os
import json

try:
    os.mkdir('Data')
except FileExistsError:
    None
except PermissionError:
    print("This program is placed in a read-only location and requires write permissions, please relocate \n")
    raise SystemExit
# checks if the Data folder exists, makes one if not, and checks if it has write perms

if os.path.exists('./Data/processed.json') == True:
    ovwr = input('The data file already exists, do you want to overwrite it? Y/N: ')
    print(ovwr)
    if ovwr == "Y" or "y":
        print("\n")
    elif ovwr == "N" or "n":
        raise SystemExit
    else: 
        print("Unknown command, try again. \n")
        raise SystemExit
else:
    None
# checks if the processed.json file already exists, warns user if yes



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


print("Your directory contains", os.listdir("./Data/"),"\n")
# lists the elements inside the Data folder

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
    
print(fileName, "\n")

path = "./Data/" + fileName
# combines the folder path to make the final path leading to the right file

print(path, "\n")

with zipfile.ZipFile(path, 'r') as dataFiles:
    # need to get rid of or ignore pdf + video file probably here, since it's where the zip is first opened
    names = dataFiles.namelist()
    print(names)
    progress = 0
    output = []
    for name in names:
        print(name, "\n")
        content = dataFiles.read(name)
        parsedData = json.loads(content)
        progress = progress + 1
        print("Progress is at", progress, "/", len(names),"\n")
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
            # removes all the unwanted information according to the True/False statements at the document start
            # stream has the final stream information as a dictionary
            #print(stream)
            output.append(stream)
            print(output)
            with open('./Data/processed.json', 'w'):
                json.dumps(output, ensure_ascii=False, indent=0)

            # dumps the current stream into a file
            # for some reason it's duplicating streams, almost like it returned to the old behaviour where it'd print every time an if statement was processed, rather than at the end
            # doesn't actually write to file, either because it doesn't finish the script (last died at 2025-11-27T22:37:15Z), or because of something else

            # right now the script works as intended, it removes all unwanted elements of the streams and prints out the result
            # next things are to not load the video file and the pdf

# save all that info in an array of some sort (helper file)
# once all the brackets are done, move to next file
# once all *files* are done, give some sort of summary

# maybe somehow turn all info into charts

    # opens the Zip file and turns the names of all files inside into a list

    # if dataFiles contains .pdf file, remove
    # need to remove the pdf - it's the last one in the list so could play around that, maybe just ignore the last

    # progress = 0
    # just a visual tracker for where it goes, might remove later
