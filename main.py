import zipfile
import os 

# basically, check the folder for an existing zip file that has "my_spotify_data" in the name
# if one doesn't exist, prompt the user to drop one in the Data folder
# once the prompt is gone, check again
# error if no file, continue if file found

#zipf.read reads zipfile (one file inside the zip)
#content.decode converts bytes -> string

# for all files in data loop this

fileName = "whatever the file is"

with zipfile.Zipfile(fileName, "r") as zipf:
    content = zipf.read(fileName)
    print(content.decode())

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