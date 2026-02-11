import queue
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import threading
from progress import progressReporter
import spotify


def helperString(string:str):
    string

progressTask = "processing/analysing/doing"
percentage = "63"
currentTask = "streamingHistory.json"
# stores/initializes variables that are used for tracking progress in the main script


def ScreenSizer():
        sizer = tk.Tk()
        screen_width = sizer.winfo_screenwidth()
        screen_height = sizer.winfo_screenheight()
        # a tool that stores screen sizes, was added to make dynamic sizing to window, but not used
        

class HelpWindow:
    def __init__(halp):
        halp.window = Tk()
        # creates the helper window

        halp.window.geometry("450x600")
        # initial set size of the window

        halp.window.rowconfigure([0,1,2,3,4,5,6,7], weight=1)
        halp.window.columnconfigure([0,1,2], weight=1)
        # configures the horizontal and vertical grid guidelines

        halp.window.configure(background="#1e1e1e")
        # background color (grey-ish black)

        halp.window.title("Help / Info")
        # title of the window

        helpText1 = ttk.Label(halp.window, text='To start the program, press one of the options on the main window. If this is your first time using the program, please press "JSON processing", since it is required for later stages', background="#1e1e1e", foreground="white", wraplength=300)
        helpText1.grid(row=1, column=1)
        # first part of the helper text

        helpText2 = ttk.Label(halp.window, text="JSON processing is the first stage - it takes your ZIP file and combines each JSON's data into one CSV as raw data", background="#1e1e1e", foreground="white", wraplength=300)
        helpText2.grid(row=2, column=1)
        # second part of the helper text

        helpText3 = ttk.Label(halp.window, text='The next stage is CSV "analysing" (parsing), where the raw CSV is transformed according to the config file', background="#1e1e1e", foreground="white", wraplength=300)
        helpText3.grid(row=3, column=1)
        # third part of the helper text

        helpText4 = ttk.Label(halp.window, text="Once the CSV is parsed, the next part calculates the numbers (number of streams, how many times tracks were skipped, etc)", background="#1e1e1e", foreground="white", wraplength=300)
        helpText4.grid(row=4, column=1)
        # fourth part of the helper text

        helpText5 = ttk.Label(halp.window, text="As the final part, the charter takes the finalized data and turns it into charts (NOT IMPLEMENTED YET)", background="#1e1e1e", foreground="white", wraplength=300)
        helpText5.grid(row=5, column=1)
        # fifth part of the helper text

        helpText5 = ttk.Label(halp.window, text="There's also the option to take the finalized data and give a short text-based summary, rather than charts", background="#1e1e1e", foreground="white", wraplength=300)
        helpText5.grid(row=6, column=1)
        # fifth part of the helper text

        helpExitButton = ttk.Button(halp.window, text="Close", command=halp.window.destroy)
        helpExitButton.grid(row=7, column=1, sticky="s", pady=15)
        # exit button at the bottom that closes the program 



class GUIWindow:
    def __init__(self):

        self.window = Tk()
        self.window.geometry("600x250+1280+720")
        # initial set size of the window



        self.window.rowconfigure([0,1,2,3,4,5,6], weight=10, minsize=25)
        self.window.columnconfigure(0, weight=5, minsize=250)
        # configures the horizontal and vertical grid guidelines

        self.window.configure(background="#1e1e1e")
        # basic customisation of the window, makes a grey-ish black background

        self.window.title("Spotify Streaming History Analyser")
        # title of the window

        self.progress = tk.IntVar()
        self.queue = queue.Queue()
        # sets up the variables needed for the progress bar

        progressBar = ttk.Progressbar(self.window, variable=self.progress, maximum=100, length=250)
        progressBar.grid(row=2, padx=20)
        # sets up the progress bar itself (maximum not referring to size, but the max %)

        branding = ttk.Label(self.window, text="Spotify Analyser v.0.1 by EllF", background="#1e1e1e", foreground="white")
        branding.grid(row=6, column=0, sticky="sw")
        # a short branding in the bottom left corner

        progressText = ttk.Label(self.window, text=f"Current Task: {progressTask}", background="#1e1e1e", foreground="white")
        progressText.grid(row=1, column=0)
        # the description of progress (task name, state, etc)

        progressName = ttk.Label(self.window, text=f"Current file: {currentTask}", background="#1e1e1e", foreground="white")
        progressName.grid(row=3, column=0)
        # the exact file being worked on (.zip, .json, .csv (or .py, if none of the others))

        progressPercent = ttk.Label(self.window, text=f"{percentage}%", background="#1e1e1e", foreground="white")
        progressPercent.grid(row=4, column=0)
        # the percentage progress of the current task

        threading.Thread(target=progressReporter(self.percentageProgress, "ya", percentage)).start()

        self.window.after(100, self.poll_queue)

    def emptyFunc():
        None

    def fileNameReporter(text, filename):
        print("Current file:", filename)

    def percentageProgress(message, percentage, extra=None):
        print("Current task progress: ", percentage,"% ", message)

    def poll_queue(self):
        try:
            while True:
                self.progress.set(self.queue.get_nowait())
        except queue.Empty:
            pass

        self.window.after(100, self.poll_queue)

    def run(self):
        self.window.mainloop()



class InputWindow:
    def __init__(user):

        def windowMoverStart(event):
            user.window._x = event.x
            user.window._y = event.y
            # function that helps the function below to move the window

        def windowMover(event):
            user.window.lift()
            user.window.focus_force()
            x = event.x_root - user.window._x
            y = event.y_root - user.window._y
            user.window.geometry(f"+{x}+{y}")
            # function that handles moving the window when, well, moved

        def customTitlebar():
            user.window.overrideredirect(True)
            # overrides the basic title window

            user.window.attributes("-topmost", True)
            user.window.update()
            user.window.attributes("-topmost", False)
            # quick fix to make sure the window doesn't accidentally go below another app when launching

            user.window.bind("<Button-1>", lambda i: user.window.lift())
            # makes sure any button press focuses the window


        ### setup of the window


        user.window = Tk()
        user.window.geometry("700x450")
        # set size of the window

        user.window.after(10, customTitlebar)
        # calls the custom title bar after loading

        user.window.title("Spotify Streaming History Analyser")
        # sets the window title when custom taskbar isn't in use

        user.window.rowconfigure([0,1,3,4,5,6,7], weight=1)
        user.window.columnconfigure([0], weight=1)
        # sets up the rows and columns (not "needed", but relic of old version)

        user.window.bind("<grave>", lambda i: user.window.destroy())
        # binds the tilde key to close the window, in case something goes wrong and need to close it without Alt+F4


        ### design of the titlebar


        titleBar = tk.Frame(user.window, background="#414141", relief="raised", height=32, width=700)
        titleBar.grid(row=0, column=0, sticky="new")
        # creates a custom title bar

        titleBar.config(cursor="hand2")
        # changes the cursor when hovering/mousing over the new title bar
        # "arrow" is default win mouse

        titleBar.columnconfigure(0, weight=1)
        titleBar.columnconfigure(1, weight=0)
        titleBar.rowconfigure(0, weight=1)
        titleBar.grid_propagate(False)
        # forces column configuration for the title bar

        titleBar.bind("<B1-Motion>", windowMover)
        titleBar.bind("<Button-1>", windowMoverStart)
        # tells windowMover/windowMoverStart to act when dragging/hovering (this means the window can only be moved via the titleBar when the custom titleBar is active)

        close = tk.Button(titleBar, text="X", background="#AC4E4E", foreground="white", width=8, command=user.window.destroy)
        close.grid(column=4, row=0, sticky="e", padx=2, pady=2)
        close.columnconfigure(4, weight=0)
        # adds back the close button to the top right corner

        titleText = tk.Label(titleBar, text="Spotify Streaming History Analyser", background="#414141", foreground="white")
        titleText.grid(column=1, row=0, sticky="w")
        titleText.config(anchor="center")
        # title of the window (when the custom titlebar is in use)


        ### design for the rest of the window


        backgroundBlock = tk.Frame(user.window, background="#1e1e1e")
        backgroundBlock.grid(row=1, column=0, sticky="nsew")
        # adds a block that the rest of the elements are placed on (apart from titleBar and its children)

        backgroundBlock.rowconfigure([0,1,2,3,4,5,6,7,8], weight=1)
        backgroundBlock.columnconfigure(0, weight=1)
        backgroundBlock.columnconfigure([1,2,3], weight=0)
        backgroundBlock.columnconfigure(4, weight=1)
        # configures the block's rows and columns

        branding = ttk.Label(backgroundBlock, text="Spotify Analyser v.0.1 by EllF", background="#1e1e1e", foreground="white")
        branding.grid(row=8, column=0, sticky="sw")
        branding.columnconfigure(0, weight=0)
        # a short branding in the bottom left corner

        prompt = tk.Label(backgroundBlock, text="Please select a task", background="#1e1e1e", foreground="white")
        prompt.grid(row=0, column=2, sticky="ew", pady=20)
        # top prompt that just tells user to click a button


        ### all the different buttons to start tasks


        process = tk.Button(backgroundBlock, text="Start JSON processing", command=lambda: user.taskStarter("processor"))
        process.grid(row=2, column=2, sticky="ew", pady=15)
        # button to start processor

        analyse = tk.Button(backgroundBlock, text="Start CSV analysing", command=lambda: user.taskStarter("analyser"))
        analyse.grid(row=3, column=2, sticky="ew", pady=15)
        # button to start analyser

        maths = tk.Button(backgroundBlock, text="Start CSV grouping", command=lambda: user.taskStarter("mathematician"))
        maths.grid(row=4, column=2, sticky="ew", pady=15)
        # button to start mathematician

        chart = tk.Button(backgroundBlock, text="Start data charting", command=lambda: user.taskStarter("charter"))
        chart.grid(row=5, column=2, sticky="ew", pady=15)
        # button to start charter (doesn't exist yet)

        summary = tk.Button(backgroundBlock, text="Create a summary", command=lambda: user.taskStarter("summary"))
        summary.grid(row=6, column=2, sticky="ew", pady=15)
        # button to start charter (doesn't exist yet)

        helpBtn = tk.Button(backgroundBlock, text="Help", command=HelpWindow, width=5)
        helpBtn.grid(row=0, column=4, sticky="ne", padx=30, pady=20)
        # button to open a help window (contains info about tasks)

        exitButton = tk.Button(backgroundBlock, text="Quit", command=user.window.destroy, width=5)
        exitButton.grid(row=7, column=2, sticky="s", pady=20)
        # exit button at the bottom that closes the program (does the same thing as the close button, but more user-friendly)



    def taskStarter(user, task):
        user.window.destroy()
        spotify.startuptask(task, progressReporter)
        GUIWindow()
        # takes the user selected task from InputWindow, starts the main function and GUIWindow, passing the task



    def run(user):
        user.window.mainloop()
        # starts the user input window



if __name__ == "__main__":
    InputWindow().run()
    # starts the user input window