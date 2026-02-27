Spotify (History) Analyser (SHA) is a small python program to analyse Spotify streaming history data locally, with configurable options for processing :) <br/>

<br/>

SHA takes your Spotify Streaming History zip file from Spotify and churns out CSV files with different levels of processing done. <br/> 

<br/>

Stage 1: Grinds down the JSON files that Spotify sends out in the history file (could be as few as 3, up to dozens) into a single JSON file (with some trimming) <br/>
Stage 2: Further trims down data according to the user configuration (via config file) and turns each individual stream into a human-readable CSV file<br/>
Stage 3: The final stage takes all the individual streams and turns them into per-song statistics <br/>
Stage 4: Provides a short, customisable summary of your listening habits. Planned feature: a tool that creates charts dynamically from source data <br/>

<br/>

In large part, SHA was created as a data-processor just for DSI (Discord Spotify Integration), and this behavior can be toggled in the config.

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