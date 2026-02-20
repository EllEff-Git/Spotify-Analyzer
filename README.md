Spotify (History) Analyser (SHA) is a small python program to analyse Spotify streaming history data locally, with configurable options for processing :) <br/>

<br/>

SHA takes your Spotify Streaming History zip file from Spotify and churns out CSV files with different levels of processing done. <br/> 

<br/>

At the lowest level, it just grinds down the dozens of JSON files that Spotify sends out in the history file into a single JSON file (with some trimming). <br/>
After that, it further trims down data according to the user configuration (included config file) and turns each individual stream into a human-readable CSV file <br/>
The final stage takes all the individual streams and turns them into per-song statistics <br/>

<br/>

The plan is to add further functionality, including a quick summary of data as well as a tool that automatically charts the data, but for now this tool exists as a servant to DSI.

<br/>

In large part, SHA was created as a data-processor just for DSI (Discord Spotify Integration), and by default, this is the way it processes the first launch (can be disabled in config).

<br/>

Example of the JSON files that Spotify ships out in their "my_streaming_history.zip" file (mine had 52 JSONs)<br/>
![Imgur Image](https://i.imgur.com/o0LBQ9p.png) <br/>
Short snippet of the DSI-configured CSV <br/>
![Imgur Image](https://i.imgur.com/kXElZzN.png) <br/>

For installation and instructions:

https://elleffnotelf.com/guides/Spotify-Analyser



```
$$$$$$$$\ $$\       $$\       
$$  _____|$$ |      $$ |      
$$ |      $$ |      $$ |      
$$$$$\    $$ |      $$ |      
$$  __|   $$ |      $$ |      
$$ |      $$ |      $$ |      
$$$$$$$$\ $$$$$$$$\ $$$$$$$$\ 
\________|\________|\________|
```