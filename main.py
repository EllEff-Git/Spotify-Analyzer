import zipfile
import os 

# basically, check the folder for an existing zip file that has "my_spotify_data" in the name
# if one doesn't exist, prompt the user to drop one in the Data folder
# once the prompt is gone, check again
# error if no file, continue if file found

print("Your directory contains", os.listdir("./Data/"))

dataArray = os.listdir("./Data")

if not dataArray:
    input("Please move your 'my_spotify_data.zip' file to the Data folder.")
    # has no files, needs user to move zip there
if 'mySpotifyData.zip' in dataArray:
    fileName = "mySpotifyData.zip"
    print("Correct file found")
    # the first file in the directory is the correct zip file
if len(dataArray) == 1:
    print(os.path.splitext(dataArray[0]))
    if ".zip" in os.path.splitext(dataArray[0]):
        fileName = dataArray[0]
        print("Attempting to use the misnamed zip file in the Data folder.")
        # uses the first available zip file in the hopes it's correct
    else:
        print("The file found in Data folder does not match the correct type, please move your 'my_spotify_data.zip' file to the Data folder.")
        raise SystemExit
        # didn't find a zip file
else:
    print("Too many files found in the Data folder, please remove unnecessary files.")
    raise SystemExit
    # the correct file wasn't found and too may files are present
    
print(fileName)

path = "./Data/" + fileName

print(path)

#zipf.read reads zipfile (one file inside the zip)
#content.decode converts bytes -> string

# for all files in data loop this

# I'll also need ZipFile.namelist() and then need to exclude the pdf and video files
# after that I'll have to loop the zipfile reading process for all the right files
"""
with zipfile.ZipFile(path, "r") as zipf:
    content = zipf.read(path)
    print(content.decode())
"""

#this is the main file that should handle most stuff

#tl;dr

# unzip the zip
# ignore the pdf and video history
# take a file
# go through the bracketed info
# save ts (timestamp), ms_played (milliseconds played), track_name, artist name, album name, shuffle and skipped
# if the track_name is null, that means it's either busted or an episode, which I don't care about
# save all that info in an array of some sort (helper file)
# once all the brackets are done, move to next file
# once all *files* are done, give some sort of summary

# maybe somehow turn all info into charts

# example song
"""
{
    "ts": "2015-02-01T18:11:45Z",
    "platform": "OS X 11.0.1 [x86 8]",
    "ms_played": 14250,
    "conn_country": "FI",
    "ip_addr": "88.112.15.25",
    "master_metadata_track_name": "Sugar",
    "master_metadata_album_artist_name": "Maroon 5",
    "master_metadata_album_album_name": "V",
    "spotify_track_uri": "spotify:track:6DrBnEWZ5kxvBiBaDaGQnc",
    "episode_name": null,
    "episode_show_name": null,
    "spotify_episode_uri": null,
    "audiobook_title": null,
    "audiobook_uri": null,
    "audiobook_chapter_uri": null,
    "audiobook_chapter_title": null,
    "reason_start": "clickrow",
    "reason_end": "fwdbtn",
    "shuffle": false,
    "skipped": true,
    "offline": false,
    "offline_timestamp": null,
    "incognito_mode": false
  },

"""