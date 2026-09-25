Spotify (History) Analyser (SHA) is a small python program to analyse Spotify streaming history data locally, with configurable options for processing :) <br/>

<br/>

SHA takes your Spotify Streaming History zip file from Spotify and churns out formatted data with different levels of processing done. <br/> 

<br/>

Stage 1: Grinds down the JSON files that Spotify sends out in the history file (could be as few as 3, up to dozens) into a single JSON file (with some trimming) <br/>
Stage 2: Further trims down data according to the user (UI-based config) and turns each individual stream into human-readable format <br/>
Stage 3: The final stage takes all the individual streams and turns them into per-song statistics, drops a .csv file ready to use elsewhere <br/>
Stage 4: Provides a short, customisable summary of your listening habits, also gives an .xlsx file <br/>
Stage 5: Creates 0-11 dynamic charts based on config + an overview page of generic stats <br/>

<br/>

In large part, SHA was created as a data processor just for DSI (Discord Spotify Integration), and there's a toggle to automatically push out DSI-compliant files.

<br/>

Example of the JSON files that Spotify ships out in their "my_streaming_history.zip" file (mine had 52 JSONs)<br/>
![Imgur Image](https://i.imgur.com/o0LBQ9p.png) <br/>

Short snippet of the DSI-configured CSV <br/>
![Imgur Image](https://i.imgur.com/kXElZzN.png) <br/>



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