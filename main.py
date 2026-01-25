import zipfile
import os
import json

try:
    os.mkdir('Data')
except FileExistsError:
    None
except PermissionError:
    print("This program is placed in a read-only location, please relocate \n")
    raise SystemExit

# quickly checks if the Data folder exists, makes one if not, and checks if it has write perms
# later will need to implement some behavior to check for already existing files made by this script


###################
# CUSTOMISATION
# these are all the different types of information that Spotify stores, turn them on/off at your leisure
# currently only songs are supported, episodes and audiobooks are skipped (videos are enabled)
#
timeStampEnabled = True
# timestamp (when the track was started)
usernameEnabled = False
# username
platformEnabled = False
# platform (Android, Chromecast, iOS, etc)
timePlayedEnabled = True
# time listened to each track (this is the main thing people want, recommended to keep on)
countryEnabled = False
# list country per track (location at the listening time)
userAgentEnabled = False
# list the streaming agent (Spotify, Firefox, etc)
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
# not currently implemented, maybe in the future.

# episodesEnabled = False
# not currently implemented, maybe in the future. 
# audiobooksEnabled = False
# not currently implemented, maybe in the future.

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
if len(dataArray) == 1:
    if ".zip" in os.path.splitext(dataArray[0]):
        fileName = dataArray[0]
        print("Attempting to use the misnamed zip file in the Data folder.\n")
        # uses the first available zip file in the hopes it's correct
    else:
        print("The file found in Data folder does not match the correct type, please move your 'my_spotify_data.zip' file to the Data folder.\n")
        raise SystemExit
        # didn't find a zip file
else:
    print("Too many files found in the Data folder, please remove unnecessary files.\n")
    raise SystemExit
    # the correct file wasn't found and too may files are present
    
print(fileName, "\n")

path = "./Data/" + fileName
# combines the folder path to make the final path leading to the right file

print(path)

with zipfile.ZipFile(path, 'r') as dataFiles:
    names = dataFiles.namelist()
    # opens the Zip file and turns the names of all files inside into a list

    # if dataFiles contains .pdf file, remove
    # need to remove the pdf - it's the last one in the list so could play around that, maybe just ignore the last
    progress = 0

    for name in names:
        print(name)
        content = dataFiles.read(name)
        parsedData = json.loads(content)
        progress = progress + 1
        print("Progress is at", progress, "/", len(names),"\n")
        break
        """
        print(parsedData[0])
        for line in parsedData:
            fields_to_remove = ["ip_addr", "ip_addr_decrypted", "episode_name", "episode_show_name", "spotify_episode_uri", "audiobook_title", "audiobook_uri", "audiobook_chapter_uri", "audiobook_chapter_title", "offline_timestamp"]
            for field in fields_to_remove:
                line.pop(field, None)
            if timeStampEnabled == False:
                line.pop("ts", None)
            if usernameEnabled == False:
                line.pop("username", None)
            if platformEnabled == False:
                line.pop("platform", None)
            if timePlayedEnabled == False:
                line.pop("ms_played", None)
            if countryEnabled == False:
                line.pop("conn_country", None)
            if userAgentEnabled == False:
                line.pop("user_agent_decrypted", None)
            if trackNameEnabled == False:
                line.pop("master_metadata_track_name", None)
            if artistNameEnabled == False:
                line.pop("master_metadata_album_artist_name", None)
            if albumNameEnabled == False:
                line.pop("master_metadata_album_album_name", None)
            if trackURLEnabled == False:
                line.pop("spotify_track_uri", None)
            if startReasonEnabled == False:
                line.pop("reason_start", None)
            if stopReasonEnabled == False:
                line.pop("reason_end", None)
            if shuffleEnabled == False:
                line.pop("shuffle", None)
            if skipEnabled == False:
                line.pop("skipped", None)
            if offlineEnabled == False:
                line.pop("offline", None)
            if incognitoEnabled == False:
                line.pop("incognito_mode", None)
            else:
                None
            
            print(line)
            break
            """
        # at this stage "parsedData" contains the full info about 1 song, each file contains a lot of songs
        # first remove the curly brackets from the start and end, and split the elements with a comma
        # parsedData = parsedData.translate(None, '{}')

# somehow have to integrate this into the parsing to check for each or find a way to merge the strings together (replace the "ts" with "timestampEnabled" for example)
# can't straight up sort as an array because some songs have stuff missing, have to individually grab lines

# save all that info in an array of some sort (helper file)
# once all the brackets are done, move to next file
# once all *files* are done, give some sort of summary

# maybe somehow turn all info into charts

# example song
"""
{
    "ts": "2015-02-01T18:11:45Z", = timeStampEnabled
    username is missing here, but is present later = usernameEnabled
    "platform": "OS X 11.0.1 [x86 8]", = platformEnabled
    "ms_played": 14250, = timePlayedEnabled
    "conn_country": "FI", = countryEnabled
    "ip_addr": "88.112.15.25", never tracked
    user agent is missing here, but is present later = userAgentEnabled
    "master_metadata_track_name": "Sugar", = tracknameenabled
    "master_metadata_album_artist_name": "Maroon 5", = artistNameEnabled
    "master_metadata_album_album_name": "V", = albumNameEnabled
    "spotify_track_uri": "spotify:track:6DrBnEWZ5kxvBiBaDaGQnc", = trackURLEnabled
    "episode_name": null, not tracked
    "episode_show_name": null, not tracked
    "spotify_episode_uri": null, not tracked
    "audiobook_title": null, not tracked
    "audiobook_uri": null, not tracked
    "audiobook_chapter_uri": null, not tracked
    "audiobook_chapter_title": null, not tracked
    "reason_start": "clickrow", reasonsEnabled
    "reason_end": "fwdbtn", reasonsEnabled
    "shuffle": false, shuffleEnabled
    "skipped": true, skipEnabled
    "offline": false, offlineEnabled
    "offline_timestamp": null, not tracked
    "incognito_mode": false = incognitoEnabled
  },

"""
