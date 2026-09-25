import zipfile, os, json, datetime, time, ast, easygui, sys, openpyxl
# Required for operation (file manipulation, selection, saving, etc)
import pandas as pd
# Required for value/file manipulation
from matplotlib import font_manager, rcParams
from pathlib import Path
# Required to change the font of the charts
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.transforms import ScaledTranslation
from matplotlib.backend_bases import MouseEvent
from matplotlib.ticker import StrMethodFormatter
from matplotlib.container import BarContainer
# Required for charting
from collections import Counter
# Required for user-config optional data counting
from typing import Any
from matplotlib.text import Text
# Required for obsessively adding type clarifications to functions
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
from SHAver import Version
# Version manager





### Version ###

SHAver = Version
"""The Spotify Analyser version (Y.M.DD.HHMM)"""





### Time Function ###

def timestamper() -> str:
    """Function that returns current time, formatted, for timestamping"""
    return time.strftime("%H:%M:%S")
    # returns formatted current time





### Directory ###

directory = os.path.dirname(sys.executable)
"""The base directory of the program, where SHA.exe resides"""
iconPath = os.path.join(sys._MEIPASS, "SHA.png")
"""The directory containing the program icon png (built-in)"""

configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "SHA")
"""The folder path that should contain all the configuration files"""
shaConfigPath = os.path.join(configFolderPath, "SHA.json")
"""The filepath to the SHA configuration file"""

finalCsvPath = os.path.join(configFolderPath, "SHA.csv")
"""The filepath to the finalised CSV file"""
summaryXlsxPath = os.path.join(configFolderPath, "summary.xlsx")
"""The filepath to the summarised .xlsx file"""

extraDataPath = os.path.join(configFolderPath, "extra.json")
"""The filepath to the extra data json file"""
fontFolderPath = os.path.join(configFolderPath, "fonts")
"""The folder path that should contain any font files"""

dsiConfigFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "DSI")
"""The folder path that should contain all the DSI configuration files"""
dsiTotalTimePath = None
"""The filepath to the totalTimes.json file for DSI"""
dsiCsvPath = None
"""The filepath to the dsi.csv file for DSI"""

dsiExists = False
"""Boolean for whether DSI is installed on the same computer"""



if os.path.exists(dsiConfigFolderPath):
# if the DSI configuration folder is valid (DSI is installed)
    dsiExists = True
    # overrides boolean to show DSI does exist
    dsiTotalTimePath = os.path.join(dsiConfigFolderPath, "totalTimes.json")
    # forms the path straight to DSI's config
    dsiCsvPath = os.path.join(dsiConfigFolderPath, "dsi.csv")
    # forms the path straight to DSI's config
else:
# DSI configuration folder doesn't exist (DSI not installed/configured)
    dsiTotalTimePath = os.path.join(configFolderPath, "totalTimes.json")
    dsiCsvPath = os.path.join(configFolderPath, "dsi.csv")
    # uses the Spotify Analyser folder instead

if not os.path.exists(fontFolderPath):
# if the font folder doesn't exist yet
    print(f"{timestamper()} | Added fonts folder in the configuration folder\n"
        f"{timestamper()} | If you'd like to use a custom font for the charts, place a font file (.otf or .ttf) in the '%localappdata%/SHA/fonts' folder\n"
        f"{timestamper()} | You can easily access the folder by clicking the '...' button in the starter window")
    os.makedirs(fontFolderPath, exist_ok=True)
    # forms the font directory (and the directories before it)





### Global Variables ###

fontList = sorted(file for file in os.listdir(fontFolderPath) if Path(file).suffix.lower() in (".ttf", ".otf"))
# only grabs files in the folder that end in .ttf or .otf, ensures it's sorted (alphabetically)

if len(fontList) > 0:
# if there's at least 1 font file
    try:
    # a lot of things could blow up here, thus try/except
        if len(fontList) > 1:
        # more than 1 font in folder
            print(f"{timestamper()} | More than one font file found, trying to use first one...")
            # user inform
        fontPath = Path(os.path.join(fontFolderPath, fontList[0]))
        # gets the 0th element in the folder
        font_manager.fontManager.addfont(fontPath)
        # adds the font to the matplotlib font manager
        fontName = font_manager.FontProperties(fname=fontPath).get_name()
        # gets the name of the font
        rcParams["font.family"] = fontName
        # overrides the default matplotlib font with one (ideally) compatible with more than just the Latin alphabet
        print(f"{timestamper()} | Using custom font family: {fontName}")
        # user inform
    except Exception as fErr:
    # something goes wrong
        print(f"{timestamper()} | Failed to use custom font due to: '{fErr}'!")
        # user inform




shaConfig = None
"""The configuration file dictionary"""
dsiExport = False
"""Whether to use the options pre-configured for DSI or not"""
runCharter = False
"""Whether to run the charter after forming a summary CSV"""
useFullPeriod = "50%"
"""How to determine summary data periods"""

cfgPlatform = True
"""The platform for each listening instance (string), boolean"""
cfgStartReason = True
"""Reason for starting track (string + counter), boolean"""
cfgEndReason = True
"""Reason for ending track (string + counter), boolean"""
cfgShuffle = True
"""Shuffle state at listening time (counter of bools), boolean"""
cfgSkipped = True
"""Whether song was skipped (counter of bools), boolean"""
cfgOffline = True
"""Offline state at listening time (counter of bools), boolean"""



### Stage 1 ###

stageOneOutput = []
"""List to hold Stage 1 output data"""

### Stage 2 ###

stageTwoOutput = []
"""List to hold the Stage 2 output data"""

### Stage 3 ###

stageThreeData = None
"""A Pandas object to store a combined dataframe from Stage 2"""
stageThreeOutput = None
"""A Pandas DataFrame to hold the Stage 3 output data"""

### Stage 4 ###

excelSheets = {}
"""A dictionary to hold all the dataframes of Spotify data"""
extraInfoDict = {}
"""A dictionary to hold all the extra (user-configured) data"""

topSelectionType = "Time"
"""How the top items should be selected (str, "Time" or "Plays")"""
topTimeFormat = "Hours"
"""How the top tracks should be calculated (str, "Seconds", "Minutes", "Hours", "Days")"""
topTrackCount = 25
"""How many songs should be picked for top tracks (int, 0-100)"""
topArtistCount = 10
"""How many artists should be picked for top artists (int, 0-100)"""
topAlbumCount = 15
"""How many albums should be picked for top albums (int, 0-100)"""
topMonthCount = 12
"""How many months should be picked for top months (int, 0-50)"""
individualMonths = False
"""Boolean for whether months are counted as individuals (eg. May 2025 vs May 2026) or as shared (May vs June)"""
topYearCount = 3
"""How many years should be picked for top years (int, 0-50)"""
topHistoricalCount = 15
"""How many tracks, artists and albums should be selected for monthly and yearly historical summaries"""





### Starter Window ###

class starterWindow(QWidget):
    """The startup window"""

    labelSwap = pyqtSignal(str)
    # A pyQt signal to swap the label
    chartSignal = pyqtSignal(dict, dict)
    """A pyQt signal to start the charting window"""

    def __init__(self):
        super().__init__()
        # init

    ### Init / Basic ###

        self.version = SHAver
        # stores the version in self
        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"Spotify (History) Analyser"
        # stores the program name

        self.windowSizeX = max(750, int(startApp.primaryScreen().size().width() / 4))
        self.windowSizeY = int(self.windowSizeX * 1.2)
        # base window sizes (dynamic, based on display res)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size minimums

    ### Layout ###

        self.mainLayout = QGridLayout()
        # a layout to use
        self.mainLayout.setContentsMargins(40, 40, 40, 40)
        # sets margins of 50px to each edge
        self.mainLayout.setColumnMinimumWidth(0, int(self.windowSizeX / 3))
        self.mainLayout.setColumnMinimumWidth(1, 150)
        self.mainLayout.setColumnMinimumWidth(2, int(self.windowSizeX / 3))
        # sets the columns 
        self.setLayout(self.mainLayout)
        # makes the window use that layout

    ### Status ###

        self.statusLabel = QLabel("Loading SHA...")
        # a simple label to indicate current progress
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers text

    ### Buttons ###

        self.buttonLayout = QGridLayout()
        # layout for the buttons to go into
        self.buttonLayout.setHorizontalSpacing(25)
        # ensures the items are 25 ? apart

        self.buttonSpacer = QSpacerItem(100, 40)
        # a smaller spacer to create gap between the inputs and the buttons

        self.startButton = QPushButton("Start")
        self.startButton.setToolTip("Save configuration and start processing")
        self.startButton.setFixedSize(130, 60)
        # button to start the analyser

        self.chartButton = QPushButton("Chart Setup")
        self.chartButton.setToolTip("Configure the summary charts' visuals\nNot implemented in this version!")
        self.chartButton.setFixedSize(90, 40)
        # button to configure charting
        self.chartButton.setEnabled(False)
        # disabled for now

        self.folderButton = QPushButton("...")
        self.folderButton.setToolTip("Open the SHA directory")
        self.folderButton.setFixedSize(90, 40)
        # button to open the folder path

        self.buttonLayout.addItem(self.buttonSpacer, 0, 0, 1, 2)
        self.buttonLayout.addWidget(self.chartButton, 1, 0)
        self.buttonLayout.addWidget(self.startButton, 1, 1)
        self.buttonLayout.addWidget(self.folderButton, 1, 2)
        # adds buttons to their layout

    ### Config Layout ###

        self.leftSideLabel = QLabel("Data Formatting Options")
        self.leftSideLabel.setToolTip("Options that change which data is collected and stored\nApplies to Stages 1-3")
        # label for the left side config
        self.rightSideLabel = QLabel("Post-Processing Options")
        self.rightSideLabel.setToolTip("Options that change how the summaries/charts are formed\nApplies to Stages 4-5")
        # label for the right side config

        self.leftSideConfig = QGridLayout()
        # layout for the left side of the config page (data formatting)
        self.rightSideConfig = QGridLayout()
        # layout for the right side of the config page (post-processing/summary)

        self.top50Validator = QIntValidator(0, 50)
        # integer validator for line edits, keeps things between 0 and 50 (99)
        self.top100Validator = QIntValidator(0, 100)
        # integer validator for line edits, keeps things between 0 and 100 (999)

    ### Left Side Config ###

        self.platformLabel = QLabel("Platform")
        self.platformLabel.setToolTip("Whether to include a platform identifier for each stream")
        self.platformCheck = QCheckBox()
        # platform option

        self.startLabel = QLabel("Start Reason")
        self.startLabel.setToolTip("Whether to include the start reason for each stream")
        self.startCheck = QCheckBox()
        # start reason option

        self.endLabel = QLabel("End Reason")
        self.endLabel.setToolTip("Whether to include the end reason for each stream")
        self.endCheck = QCheckBox()
        # end reason option

        self.shuffleLabel = QLabel("Shuffle")
        self.shuffleLabel.setToolTip("Whether to include shuffle state for each stream")
        self.shuffleCheck = QCheckBox()
        # shuffle option

        self.skippedLabel = QLabel("Skipped")
        self.skippedLabel.setToolTip("Whether to include the skip state for each stream")
        self.skippedCheck = QCheckBox()
        # skipped option

        self.offlineLabel = QLabel("Offline")
        self.offlineLabel.setToolTip("Whether to include the offline state for each stream")
        self.offlineCheck = QCheckBox()
        # offline option

        self.leftSideConfig.addWidget(self.platformLabel, 2, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.leftSideConfig.addWidget(self.platformCheck, 3, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # platform
        self.leftSideConfig.addWidget(self.startLabel, 4, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.leftSideConfig.addWidget(self.startCheck, 5, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # start
        self.leftSideConfig.addWidget(self.endLabel, 6, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.leftSideConfig.addWidget(self.endCheck, 7, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # end
        self.leftSideConfig.addWidget(self.shuffleLabel, 8, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.leftSideConfig.addWidget(self.shuffleCheck, 9, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # shuffle
        self.leftSideConfig.addWidget(self.skippedLabel, 10, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.leftSideConfig.addWidget(self.skippedCheck, 11, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # skipped
        self.leftSideConfig.addWidget(self.offlineLabel, 12, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.leftSideConfig.addWidget(self.offlineCheck, 13, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # offline

    ### Right Side Config ###

        self.topSelectionLabel = QLabel("Top Calculation Type")
        self.topSelectionLabel.setToolTip("How to calculate the top items\nTime uses playtime per item to rank\nPlays takes the number of times the item appeared to rank")
        self.topSelectionDrop = QComboBox()
        self.topSelectionOptions = ["Time", "Plays"]
        self.topSelectionDrop.setMaximumWidth(250)
        # ranking calculation (time vs count)

        self.topTimeFormatLabel = QLabel("Time Format")
        self.topTimeFormatLabel.setToolTip("What time format to display in the summary\nRankings are performed at a millisecond accuracy level, this is just for visuals")
        self.topTimeFormatDrop = QComboBox()
        self.topTimeFormatOptions = ["Seconds", "Minutes", "Hours", "Days"]
        self.topTimeFormatDrop.setMaximumWidth(250)
        # time division

        self.topTrackLabel = QLabel("Top Tracks")
        self.topTrackLabel.setToolTip("How many tracks to display in the summary\n0-100, 0 disables top tracks")
        self.topTrackLine = QLineEdit()
        self.topTrackLine.setValidator(self.top100Validator)
        self.topTrackLine.setMaximumWidth(250)
        # track count

        self.topArtistLabel = QLabel("Top Artists")
        self.topArtistLabel.setToolTip("How many artists to display in the summary\n0-100, 0 disables top artists")
        self.topArtistLine = QLineEdit()
        self.topArtistLine.setValidator(self.top100Validator)
        self.topArtistLine.setMaximumWidth(250)
        # artist count

        self.topAlbumLabel = QLabel("Top Albums")
        self.topAlbumLabel.setToolTip("How many albums to display in the summary\n0-100, 0 disables top albums")
        self.topAlbumLine = QLineEdit()
        self.topAlbumLine.setValidator(self.top100Validator)
        self.topAlbumLine.setMaximumWidth(250)
        # album count

        self.topMonthTypeLabel = QLabel("Month Calculation Type")
        self.topMonthTypeLabel.setToolTip("How to calculate top months\nIndividual counts each month of each year as its own item\nShared counts all instances of a month across years")
        self.topMonthTypeDrop = QComboBox()
        self.topMonthTypeOptions = ["Individual", "Shared"]
        self.topMonthTypeDrop.setMaximumWidth(250)
        # month type

        self.topMonthCountLabel = QLabel("Top Months")
        self.topMonthCountLabel.setToolTip("How many months to display in the summary\n0-50, 0 disables top months\nIf using shared months, caps at 12 (each month can then display)")
        self.topMonthCountLine = QLineEdit()
        self.topMonthCountLine.setValidator(self.top50Validator)
        self.topMonthCountLine.setMaximumWidth(250)
        # month count

        self.topYearLabel = QLabel("Top Years")
        self.topYearLabel.setToolTip("How many years to display in the summary\n0-50, 0 disables top years\nThe real cap is determined by your account data history, setting this over that will show all available years")
        self.topYearLine = QLineEdit()
        self.topYearLine.setValidator(self.top50Validator)
        self.topYearLine.setMaximumWidth(250)
        # year count

        self.summaryCountLabel = QLabel("Historical Tops")
        self.summaryCountLabel.setToolTip("How many tracks, artists and albums to select from the last month and year of data\n0-50, 0 disables historical tops")
        self.summaryCountLine = QLineEdit()
        self.summaryCountLine.setValidator(self.top50Validator)
        self.summaryCountLine.setMaximumWidth(250)
        # year/month top count

        self.useFullPeriodLabel = QLabel("Full Dates")
        self.useFullPeriodLabel.setToolTip("How to determine the summary data points\n"
                                           "Full uses the last full month and year of data (eg. if the data stops on the 15th of September, falls back to August)\n"
                                           "Current uses the current month and year of data (will result in less data, especially if running early in the year or month)\n"
                                           f"The percentage options use the current month and year, if the period is at least x% complete, otherwise falls back to previous period")
        self.useFullPeriodDrop = QComboBox()
        self.useFullPeriodOptions = ["Full", "Current", "33%", "50%", "66%", "75%", "90%"]
        self.useFullPeriodDrop.setMaximumWidth(250)
        # date selection

        self.rightSideConfig.addWidget(self.topSelectionLabel, 2, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.topSelectionDrop, 3, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # top calculation type
        self.rightSideConfig.addWidget(self.topTimeFormatLabel, 4, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.topTimeFormatDrop, 5, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # time format
        self.rightSideConfig.addWidget(self.topTrackLabel, 6, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.topTrackLine, 7, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # top tracks
        self.rightSideConfig.addWidget(self.topArtistLabel, 8, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.topArtistLine, 9, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # top artists
        self.rightSideConfig.addWidget(self.topAlbumLabel, 10, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.topAlbumLine, 11, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # top albums
        self.rightSideConfig.addWidget(self.topMonthTypeLabel, 12, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.topMonthTypeDrop, 13, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # month calculation type
        self.rightSideConfig.addWidget(self.topMonthCountLabel, 14, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.topMonthCountLine, 15, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # top months
        self.rightSideConfig.addWidget(self.topYearLabel, 16, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.topYearLine, 17, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # top years
        self.rightSideConfig.addWidget(self.summaryCountLabel, 18, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.summaryCountLine, 19, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # top summary numbers
        self.rightSideConfig.addWidget(self.useFullPeriodLabel, 20, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.rightSideConfig.addWidget(self.useFullPeriodDrop, 21, 0, alignment=Qt.AlignmentFlag.AlignTop)
        # full date period

    ### Bottom Config ###

        self.bottomConfig = QGridLayout()
        # bottom of the config area
        self.bottomConfig.setHorizontalSpacing(40)
        # ensures all items are 40 ? apart

        self.dsiExportLabel = QLabel("DSI Export")
        self.dsiExportLabel.setToolTip("Ignore other options and run the analyser with DSI requirements\nStops after Stage 3 (can't run summary/charts after)\nProduces a completely valid snapshot with generally useful options, even if not using with DSI")
        self.dsiExportCheck = QCheckBox()
        # DSI export (preset options)

        self.summaryLabel = QLabel("Summary Only")
        self.summaryLabel.setToolTip("Skip processing stages and form a summary based on data\nRequires at least 1 full run of SHA (without DSI Export) prior")
        self.summaryCheck = QCheckBox()
        # summary options (skip processing steps)
        self.summaryValid = False
        self.summaryCheck.setEnabled(False)
        # safeguards to ensure it can be ran, before the program runs something it can't

        self.chartOnlyLabel = QLabel("Chart Only")
        self.chartOnlyLabel.setToolTip("Skip processing stages and summary, presents summary data in chart form\nRequires at least 1 full run of SHA (without DSI Export) prior")
        self.chartOnlyCheck = QCheckBox()
        # chart options
        self.chartOnlyCheck.setEnabled(False)
        # safeguard

        self.charterLabel = QLabel("Enable Charter")
        self.charterLabel.setToolTip("Whether to enable the chart-drawing after the summary (Stage 5)\nRuns automatically after summary, if enabled")
        self.charterCheck = QCheckBox()
        # charter options

        self.dsiExportCheck.checkStateChanged.connect(lambda: self.disableOptions("DSI"))
        self.summaryCheck.checkStateChanged.connect(lambda: self.disableOptions("Summary"))
        self.chartOnlyCheck.checkStateChanged.connect(lambda: self.disableOptions("Chart"))
        # connects the checkboxes to the visual checker function

        self.bottomConfig.addWidget(self.dsiExportLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomConfig.addWidget(self.dsiExportCheck, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomConfig.addWidget(self.summaryLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomConfig.addWidget(self.summaryCheck, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomConfig.addWidget(self.chartOnlyLabel, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomConfig.addWidget(self.chartOnlyCheck, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomConfig.addWidget(self.charterLabel, 0, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomConfig.addWidget(self.charterCheck, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all the final config options to bottom config

    ### Layout Placement ###

        self.mainLayout.addWidget(self.statusLabel, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the status label to the very top

        self.mainLayout.addWidget(self.leftSideLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.rightSideLabel, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mainLayout.addLayout(self.leftSideConfig, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addLayout(self.rightSideConfig, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the left and right side config sections

        self.mainLayout.addLayout(self.bottomConfig, 3, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the bottom config

        self.mainLayout.addLayout(self.buttonLayout, 4, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the main layout

    ### Run ###

        self.labelSwap.connect(self.statusLabelSwap)
        # connects the pyqt signal to the function responsible for swapping the status label
        self.chartSignal.connect(self.startCharterWindow)
        # connects the pyqt signal to the function responsible for starting the charter window
        self.chartButton.clicked.connect(lambda: print("yo"))
        # does nothing functional yet, will later run the chart configuration (visuals)
        self.startButton.clicked.connect(self.startSHAprocess)
        # connects the buttons to their commands
        self.folderButton.clicked.connect(lambda: os.startfile(configFolderPath))
        # opens the directory where the files need to go to)

        self.summaryValidCheck()
        # runs the summary-only state check
        QTimer.singleShot(50, self.shaConfigManager)
        # runs the SHA configuration manager when the UI is done loading
        QTimer.singleShot(50, self.show)
        # once the UI is done, shows the window

### Status Label Swap ###

    def statusLabelSwap(self, text:str):
        """Function to change the current status label"""
        self.statusLabel.setText(text)
        # sets the text to match

### Check Summary Pre-requisites

    def summaryValidCheck(self):
        """Function to check if a summary-only run can be done"""

        if os.path.exists(finalCsvPath):
        # checks if the prerequisite file exists for summary-only run
            self.summaryValid = True
            # sets the boolean to True, allowing summary-only runs
            self.summaryCheck.setEnabled(True)
            self.chartOnlyCheck.setEnabled(True)
            # enables the checkboxes

### SHA Config ###

    def shaConfigManager(self):
        """Function that manages the SHA configuration"""
        global shaConfig
        # global -> local

        self.labelSwap.emit("Checking SHA configuration...")
        # user inform

        if os.path.exists(shaConfigPath):
        # if the config file exists
            try:
            # tries to read the config file (try because it could fail)
                with open(shaConfigPath, "r", encoding="utf-8") as shaCfg:
                # opens the SHA config
                    shaConfig = json.load(shaCfg)
                    # stores the loaded config
                    self.shaConfigRead()
                    # runs the config reader
            except:
            # if the file can't be found/opened
                self.shaConfigRun()
                # runs the configuration
        else:
        # file doesn't exist
            self.shaConfigRun()
            # runs the configuration

    def shaConfigRead(self):
        """Function that reads the config file"""
        global cfgPlatform, cfgStartReason, cfgEndReason, cfgShuffle, cfgSkipped, cfgOffline, runCharter, dsiExport, useFullPeriod
        global topSelectionType, topTrackCount, topTimeFormat, topArtistCount, topAlbumCount, topMonthCount, topYearCount, topHistoricalCount, individualMonths
        # global -> local

        cfgPlatform = bool(shaConfig.get("platform", False))
        cfgStartReason = bool(shaConfig.get("startR", False))
        cfgEndReason = bool(shaConfig.get("endR", False))
        cfgShuffle = bool(shaConfig.get("shuffle", False))
        cfgSkipped = bool(shaConfig.get("skipped", False))
        cfgOffline = bool(shaConfig.get("offline", False))
        # gets all the top option variables from the config

        topSelectionType = str(shaConfig.get("topSelectionType", "Time"))
        topTrackCount = int(shaConfig.get("topTrackCount", 25))
        topTimeFormat = str(shaConfig.get("topTimeFormat", "Hours"))
        topArtistCount = int(shaConfig.get("topArtistCount", 10))
        topAlbumCount = int(shaConfig.get("topAlbumCount", 15))
        topMonthCount = int(shaConfig.get("topMonthCount", 12))
        topYearCount = int(shaConfig.get("topYearCount", 3))
        topHistoricalCount = int(shaConfig.get("topHistoryCount", 15))
        individualMonths = bool(shaConfig.get("individualMonths", False))
        runCharter = bool(shaConfig.get("runCharter", True))
        dsiExport = bool(shaConfig.get("dsiExport", False))
        useFullPeriod = str(shaConfig.get("fullDates", "50%"))
        # gets all the bottom option variables from the config

        self.shaConfigPlace()
        # runs the config placer to place the values

    def shaConfigRun(self):
        """Function that displays the configuration options"""
        global shaConfig
        # global -> local

        if shaConfig is None:
        # if the config doesn't exist yet
            shaConfig = {
                "platform": False,
                "startR": False,
                "endR": False,
                "shuffle": False,
                "skipped": False,
                "offline": False,
                "topSelectionType": "Time",
                "topTrackCount": 25,
                "topTimeFormat": "Hours",
                "topArtistCount": 10,
                "topAlbumCount": 15,
                "topMonthCount": 12,
                "topYearCount": 3,
                "topHistoryCount": 15,
                "individualMonths": False,
                "runCharter": True,
                "dsiExport": False,
                "fullDates": "50%"
            }
            # forms a new, default configuration

        self.shaConfigRead()
        # runs the config reader -> uses the new variable values -> element matching

    def shaConfigPlace(self):
        """Function that passes read/default values to the option window"""

        self.labelSwap.emit("Setting configured options...")
        # user inform

        self.platformCheck.setChecked(cfgPlatform)
        self.startCheck.setChecked(cfgStartReason)
        self.endCheck.setChecked(cfgEndReason)
        self.shuffleCheck.setChecked(cfgShuffle)
        self.skippedCheck.setChecked(cfgSkipped)
        self.offlineCheck.setChecked(cfgOffline)
        # sets the left side variables

        self.topTrackLine.setText(str(topTrackCount))
        self.topArtistLine.setText(str(topArtistCount))
        self.topAlbumLine.setText(str(topAlbumCount))
        self.topMonthCountLine.setText(str(topMonthCount))
        self.topYearLine.setText(str(topYearCount))
        self.summaryCountLine.setText(str(topHistoricalCount))
        self.charterCheck.setChecked(runCharter)
        self.dsiExportCheck.setChecked(dsiExport)
        # sets the right side/bottom variables

        if individualMonths:
        # if the boolean is True (individual)
            self.topMonthTypeDrop.addItem("Individual")
            self.topMonthTypeDrop.addItem("Shared")
            # adds in "default" order
        else:
        # boolean is False (shared)
            self.topMonthTypeDrop.addItem("Shared")
            self.topMonthTypeDrop.addItem("Individual")
            # adds in the reverse order

        self.useFullPeriodDrop.addItem(useFullPeriod)
        # adds the selected item first (to make it default selected)
        self.useFullPeriodOptions.remove(useFullPeriod)
        # removes it from the list of options
        self.useFullPeriodDrop.addItems(self.useFullPeriodOptions)
        # adds the remaining items via list
        
        self.topTimeFormatDrop.addItem(topTimeFormat)
        # adds the selected item first (to make it default selected)
        self.topTimeFormatOptions.remove(topTimeFormat)
        # removes it from the list of options
        self.topTimeFormatDrop.addItems(self.topTimeFormatOptions)
        # adds the remaining items via the list

        self.topSelectionDrop.addItem(topSelectionType)
        # adds the selected item first (to make it default selected)
        self.topSelectionOptions.remove(topSelectionType)
        # removes it from the list of options
        self.topSelectionDrop.addItems(self.topSelectionOptions)
        # adds the remaining items via the list

        self.labelSwap.emit("Please configure your Spotify Analyser options\nFor any extra information, hover over any text field!")
        # user inform label

    def shaConfigWrite(self):
        """Function that grabs the currently set options and stores them globally + in-file"""
        global shaConfig, cfgPlatform, cfgStartReason, cfgEndReason, cfgShuffle, cfgSkipped, cfgOffline, runCharter, dsiExport, useFullPeriod
        global topSelectionType, topTrackCount, topTimeFormat, topArtistCount, topAlbumCount, topMonthCount, topYearCount, topHistoricalCount, individualMonths
        # global -> local

        cfgPlatform = self.platformCheck.isChecked()
        cfgStartReason = self.startCheck.isChecked()
        cfgEndReason = self.endCheck.isChecked()
        cfgShuffle = self.shuffleCheck.isChecked()
        cfgSkipped = self.skippedCheck.isChecked()
        cfgOffline = self.offlineCheck.isChecked()
        runCharter = self.charterCheck.isChecked()
        dsiExport = self.dsiExportCheck.isChecked()
        # grabs all the checkbox statuses (booleans)

        for lineedit in [self.topTrackLine, self.topArtistLine, self.topAlbumLine]:
        # goes through every line of the top 100-allowed lines
            self.checkIntValid(lineedit, 100)
            # runs the function to check + enforce the integer validators

        for lineedit in [self.topYearLine, self.summaryCountLine, self.topMonthCountLine]:
        # goes through every line of the top 50-allowed lines
            self.checkIntValid(lineedit, 50)
            # runs the function to check + enforce the integer validators

        useFullPeriod = self.useFullPeriodDrop.currentText()
        topSelectionType = self.topSelectionDrop.currentText()
        topTrackCount = int(self.topTrackLine.text())
        topTimeFormat = self.topTimeFormatDrop.currentText()
        topArtistCount = int(self.topArtistLine.text())
        topAlbumCount = int(self.topAlbumLine.text())
        topMonthCount = int(self.topMonthCountLine.text())
        topYearCount = int(self.topYearLine.text())
        topHistoricalCount = int(self.summaryCountLine.text())
        # grabs all the different dropdown/line texts (converts to int, if applicable)
        individualMonths = bool(self.topMonthTypeDrop.currentText() == "Individual")
        # checks if the selected month sorting style matches 'Individual' or not

        shaConfig = {
            "platform": cfgPlatform,
            "startR": cfgStartReason,
            "endR": cfgEndReason,
            "shuffle": cfgShuffle,
            "skipped": cfgSkipped,
            "offline": cfgOffline,
            "topSelectionType": topSelectionType,
            "topTrackCount": topTrackCount,
            "topTimeFormat": topTimeFormat,
            "topArtistCount": topArtistCount,
            "topAlbumCount": topAlbumCount,
            "topMonthCount": topMonthCount,
            "topYearCount": topYearCount,
            "topHistoryCount": topHistoricalCount,
            "individualMonths": individualMonths,
            "runCharter": runCharter,
            "dsiExport": dsiExport,
            "fullDates": useFullPeriod
        }
        # forms the configuration based on the user-configured options

        with open(shaConfigPath, "w", encoding="utf-8") as shaCfg:
        # opens the SHA config
            json.dump(shaConfig, shaCfg, indent=3)
            # dumps the config to file

### Check Integer Validators ###

    def checkIntValid(self, lineEdit: QLineEdit, cap:int):
        """Function to enforce integer validator rules"""

        try:
        # tries (the line could be empty)
            lineText = int(lineEdit.text())
            # gets the text of the given QLineEdit line, converts to int
        except:
        # if there's an error
            lineText = 0
            # uses 0 instead (doesn't generate)

        lineText = max(0, min(lineText, cap))
        # ensures the line ends up with *a* valid number, doesn't let it exceed cap
        lineEdit.setText(str(lineText))
        # sets the line text to match the calculated int

### Disable Other Options ###

    def disableOptions(self, preset:str):
        """Function to disable all non-bottom config option checkboxes"""

        checkboxStatus = True
        # default value of True to not brick anything

        if preset == "DSI":
        # if calling for DSI preset (disables top options, since DSI has requirements)
            checkboxStatus = not (self.dsiExportCheck.isChecked())
            # grabs the current bool status, reverses it (if DSI is on, everything under here should be off and vice versa)
            if self.dsiExportCheck.isChecked():
            # if the DSI export is now on, disables the summary and charter-only options
                self.summaryCheck.setChecked(False)
                self.summaryCheck.setEnabled(False)
                self.chartOnlyCheck.setChecked(False)
                self.chartOnlyCheck.setEnabled(False)
                # disables the other buttons
                self.labelSwap.emit("DSI Export enabled!\nConfigurable options disabled (using DSI preset)")
                # user inform
            else:
            # otherwise releases the summary
                if self.summaryValid:
                # if the summary-/chart-only modes can be enabled
                    self.summaryCheck.setEnabled(True)
                    self.chartOnlyCheck.setEnabled(True)
                    # release
                self.labelSwap.emit("DSI Export disabled!")
                # user inform

        elif preset == "Summary":
        # if calling for a summary-only run (can't modify options in this case)
            checkboxStatus = not (self.summaryCheck.isChecked())
            # grabs the current bool status, reverses it (if summary is on, everything under here should be off and vice versa)
            if self.summaryCheck.isChecked():
            # if the summary-only mode is on, disables the DSI export and charter-only options
                self.dsiExportCheck.setChecked(False)
                self.dsiExportCheck.setEnabled(False)
                self.chartOnlyCheck.setChecked(False)
                self.chartOnlyCheck.setEnabled(False)
                # disables the other buttons
                self.labelSwap.emit("Summary-only mode enabled!\nConfigurable options disabled (skipping processing)")
                # user inform
            else:
            # otherwise releases export
                self.dsiExportCheck.setEnabled(True)
                # release
                if self.summaryValid:
                # if the summary-/charter-only modes can be enabled
                    self.summaryCheck.setEnabled(True)
                    self.chartOnlyCheck.setEnabled(True)
                    # release
                self.labelSwap.emit("Summary-only mode disabled!")
                # user inform

        elif preset == "Chart":
        # if calling for a charter-only run (can't modify regular options in this case)
            checkboxStatus = not (self.chartOnlyCheck.isChecked())
            # grabs the current bool status, reverses it (if charter is on, everything under here should be off and vice versa)
            if self.chartOnlyCheck.isChecked():
            # if the charter-only mode is now on, disables the DSI export and summary options
                self.dsiExportCheck.setChecked(False)
                self.dsiExportCheck.setEnabled(False)
                self.summaryCheck.setChecked(False)
                self.summaryCheck.setEnabled(False)
                # disables the other buttons
                self.labelSwap.emit("Charter-only mode enabled!\nConfigurable options disabled (skipping processing)")
                # user inform
            else:
            # otherwise releases export
                self.dsiExportCheck.setEnabled(True)
                # release
                if self.summaryValid:
                # if the summary-/charter-only modes can be enabled
                    self.summaryCheck.setEnabled(True)
                    self.chartOnlyCheck.setEnabled(True)
                    # release
                self.labelSwap.emit("Charter-only mode disabled!")
                # user inform

        self.platformCheck.setEnabled(checkboxStatus)
        self.startCheck.setEnabled(checkboxStatus)
        self.endCheck.setEnabled(checkboxStatus)
        self.shuffleCheck.setEnabled(checkboxStatus)
        self.skippedCheck.setEnabled(checkboxStatus)
        self.offlineCheck.setEnabled(checkboxStatus)
        # sets all the user-configurable options on/off based on the status of the special run modes

        QApplication.processEvents()
        # forces the window to redraw (sets the checkboxes accordingly)

### Start SHA Processing ###

    def startSHAprocess(self):
        """Function to transition from config -> SHA work"""

        self.labelSwap.emit("Starting SHA...")
        # user inform
        startStage = 0
        # int to start the stage (allows window to hide before starting processing)

        if self.summaryCheck.isChecked():
        # if the summary-only mode is selected
            if self.summaryValid:
            # if the summary-only mode can be ran
                startStage = 4
                # starts at Stage Four (summary)
            else:
            # summary-only can't be ran (no data)
                self.labelSwap.emit("Summary-only mode not available!\nPlease run the program normally at least once to generate required data!")
                # user inform
                return
                # stop

        elif self.dsiExportCheck.isChecked():
        # if DSI export mode is selected
            startStage = 1
            # starts at Stage One (using DSI preset options)

        elif self.chartOnlyCheck.isChecked():
        # charter-only mode is selected
            startStage = 5
            # starts at Stage Five (skips everything, charts)

        else:
        # no override is on, processing with user-config
            startStage = 1
            # starts at Stage One (default start)

        if startStage != 0:
        # if the startStage has been set (not 0 anymore)

            self.shaConfigWrite()
            # calls the global re-assigner/config-writer

            stageStarter(startStage)
            # runs the starter with the given stage

### Charter Starter ###

    def startCharterWindow(self, excelDict: dict, additional:dict):
        """Function to start the charter window class and pass the parameters from Stage 5"""
        self.chartWindow = ChartWindow(excelDict, additional)
        # instantiates the chart window with the dataframes/dict
        self.chartWindow.destroyed.connect(self.close)
        # when the chart window is closed, closes the starterwindow (whole executable), too





### Charter ###

class ChartWindow(QMainWindow):
    """Charter window class"""

    def __init__(self, excel:dict[str, pd.DataFrame], additional:dict[str, dict]):
    # startup, requires passed data 
        super().__init__()
        # start

    ### Init / Basic ###

        self.version = SHAver
        # stores the version in self
        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"Spotify History Charter"
        # stores the program name

        self.windowSizeX = 1280
        self.windowSizeY = 720
        # stores the window sizes

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size minimums

        self.excelSheets = excel
        self.additional = additional
        # stores the dictionaries in self

        if topSelectionType == "Plays":
        # if the selected method is to get the songs by playcount
            self.sortColumn = "Playcount"
            # uses the playcount as the column to rank with
        else:
        # if not playcount -> time 
            self.sortColumn = "Total Time"
            # uses the total time as the column to rank with

        self.pages = {}
        # empty dictionary to swap between charts
        self.rankingPages = {}
        # empty dict for the rank charts to end up in
        self.rankingScrolls = {}
        # empty dict for the rank charts' scroll areas to end up in

        self.pageStack = QStackedWidget()
        # a stacked widget, allows for swapping between "pages"
        self.mainWidget = QWidget()
        # the main widget to use as the base
        self.mainLayout = QGridLayout(self.mainWidget)
        # main layout

        self.mainLayout.setSpacing(10)
        self.mainLayout.setContentsMargins(25,25,25,25)
        # sets spacing rules

        self.setStyleSheet("""
            QGroupBox {
                border: 3px solid white;
                border-radius: 8px;
                margin-top: 8px;
            }
        """)
        # modifies the group box stylesheet (used in every page) -> makes the borders thicker, ensures stuff doesn't touch the top
        
        self.dropdownLayout = QGridLayout()
        # a layout for the dropdown selector(s) to sit in

        self.chartDropdown = QComboBox()
        # a dropdown menu to select chart 
        self.chartDropdown.setFixedSize(250, 40)
        # sets fixed size

        self.dataframeDropdown = QComboBox()
        # adds a dropdown menu for the dataframe data charts only
        self.dataframeDropdown.setFixedSize(250, 40)
        # sets fixed size (smaller than the main dropdown)

        self.dropdownLayout.addWidget(self.chartDropdown, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds the main chart dropdown selector to the layout
        self.dropdownLayout.addWidget(self.dataframeDropdown, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds that dropdown to the dropdown layout

        self.mainLayout.addLayout(self.dropdownLayout, 0, 0, 1, 1)
        # adds the dropdown layout to the main layout (to the top)
        self.mainLayout.addWidget(self.pageStack, 1, 0, 1, 2)
        # makes the main layout use the page stack
        self.setCentralWidget(self.mainWidget)
        # makes the central widget the actual central widget

        self.hoveredText = None
        # variable to store what text label is being hovered over (prevents re-rendering)

    ### Run ###

        self.chartDropdown.currentTextChanged.connect(self.swapChart)
        # connects the dropdown changing to the chart swapping function
        self.dataframeDropdown.currentTextChanged.connect(self.swapRankingChart)
        # connects the secondary dropdown changing to the ranking chart swapping function

        print(f"{timestamper()} | Drawing charts...\n")
        # user inform
        QTimer.singleShot(50, self.drawOverview)
        # calls the overview creator

### Overview Page ###

    def drawOverview(self):
        """Function to create the overview page"""

        self.overviewPage = QWidget()
        # a page for the overview screen
        self.pageStack.addWidget(self.overviewPage)
        # adds the page to the stack

        self.overviewPageLayout = QGridLayout(self.overviewPage)
        # makes a layout for the page

        self.leftTopBox = QGroupBox()
        self.leftTopBox.setMaximumHeight(125)
        self.overviewTopBox = QGroupBox()
        self.overviewTopBox.setMaximumHeight(125)
        self.rightTopBox = QGroupBox()
        self.rightTopBox.setMaximumHeight(125)
        # adds group boxes to the top for each col

        self.leftSideBox = QGroupBox()
        self.overviewBox = QGroupBox()
        self.rightSideBox = QGroupBox()
        # adds group boxes for each col

        self.leftSideTopLayout = QVBoxLayout(self.leftTopBox)
        self.mainOverviewTopLayout = QVBoxLayout(self.overviewTopBox)
        self.rightSideTopLayout = QVBoxLayout(self.rightTopBox)
        # the top box layouts

        self.leftSideOverviewLayout = QVBoxLayout(self.leftSideBox)
        self.leftSideOverviewLayout.setSpacing(10)
        self.leftSideOverviewLayout.setContentsMargins(12, 24, 12, 24)
        # the left side bottom layout
        self.mainOverviewLayout = QVBoxLayout(self.overviewBox)
        self.mainOverviewLayout.setSpacing(10)
        self.mainOverviewLayout.setContentsMargins(12, 24, 12, 24)
        # the middle bottom layout
        self.rightSideOverviewLayout = QVBoxLayout(self.rightSideBox)
        self.rightSideOverviewLayout.setSpacing(10)
        self.rightSideOverviewLayout.setContentsMargins(12, 24, 12, 24)
        # the right side bottom layout

        columnWidth = int((self.windowSizeX / 3) - 90)
        # calculates a roughly 1/3rd size width for the window

        self.overviewPageLayout.setColumnMinimumWidth(0, columnWidth)
        self.overviewPageLayout.setColumnMinimumWidth(1, columnWidth)
        self.overviewPageLayout.setColumnMinimumWidth(2, columnWidth)
        # ensures all columns use the same size

        self.overviewPageLayout.setColumnStretch(0, 0)
        self.overviewPageLayout.setColumnStretch(1, 0)
        self.overviewPageLayout.setColumnStretch(2, 0)
        # ensures none of the columns stretch

        self.overviewPageLayout.setHorizontalSpacing(25)
        self.overviewPageLayout.setVerticalSpacing(10)
        # enforces the spacing between the boxes

        self.overviewPageLayout.addWidget(self.leftTopBox, 0, 0)
        self.overviewPageLayout.addWidget(self.overviewTopBox, 0, 1)
        self.overviewPageLayout.addWidget(self.rightTopBox, 0, 2)
        # adds the top box layouts to the page

        self.overviewPageLayout.addWidget(self.leftSideBox, 1, 0)
        self.overviewPageLayout.addWidget(self.overviewBox, 1, 1)
        self.overviewPageLayout.addWidget(self.rightSideBox, 1, 2)
        # adds the layouts to the page's layout

        self.pageStack.setCurrentWidget(self.overviewPage)
        # sets the active widget to be the overview page

    ### Total ###

        totalData = self.additional["Total"]
        # grabs the nested dictionary for the total data

        totalStart = pd.Timestamp(totalData["Start"])
        # grabs the start of the total period, turns back into timestamp
        totalEnd = pd.Timestamp(totalData["End"])
        # grabs the end of the total period, turns back into timestamp

        totalPeriod = f"{totalStart.day}.{totalStart.month}.{totalStart.year} - {totalEnd.day}.{totalEnd.month}.{totalEnd.year}"
        # forms a string for the total date period
        totalPlaycount = int(totalData["Playcount"])
        # grabs the total playcount (int)
        totalPlaytime = int(totalData["Playtime"])
        # grabs the total playtime (int)

        totalOver10 = int(totalData["Over10"])
        # grabs the number of plays over 10 seconds (int)
        totalOver60 = int(totalData["Over60"])
        # grabs the number of plays over 60 seconds (int)
        totalAverage = str(totalData["Average"])
        # grabs the average track duration (MM:SS)

        totalPercent = str(totalData["Percent"])
        # grabs the percentage
        self.totalDivisor = int(totalData["Divisor"])
        # grabs the time divisor
        self.totalFormat = str(totalData["Format"])
        # grabs the preferred time format
        self.individualMonths = bool(totalData["Individual Months"])
        # grabs the month calculation logic boolean

        uniqueTracks = int(totalData["Tracks"])
        uniqueArtists = int(totalData["Artists"])
        uniqueAlbums = int(totalData["Albums"])
        # grabs the unique track, artist and album counts

        self.totalTitleLabel = QLabel(f"All Spotify statistics\n({totalPeriod})")
        self.totalTitleLabel.setStyleSheet("font-size: 20px; font-weight: bold; font-style: italic;")
        self.totalTitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title

        self.totalPlaysLabel = QLabel(f"Total streams: {totalPlaycount:,.0f}")
        self.totalPlaysLabel.setToolTip("How many Spotify tracks were played over the course of the whole streaming history period")
        self.totalPlaysLabel.setStyleSheet("font-size: 16px; font-weight: bold; font-style: italic;")
        self.totalPlaysLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # plays
        
        self.totalTimeLabel = QLabel(f"Listening time: {(totalPlaytime / self.totalDivisor):,.0f} {self.totalFormat.lower()}")
        self.totalTimeLabel.setToolTip("How long you've spent listening to Spotify (all-time)")
        self.totalTimeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # time

        self.uniqueLabel = QLabel(f"Tracks: {uniqueTracks:,.0f}, Artists: {uniqueArtists:,.0f}, Albums: {uniqueAlbums:,.0f}")
        self.uniqueLabel.setToolTip("How many unique tracks, artists and albums you've listened to")
        self.uniqueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # uniques

        self.totalOver10Label = QLabel(f"Streams over 10 seconds: {totalOver10:,.0f}")
        self.totalOver10Label.setToolTip("How many of the total streams lasted for over 10 seconds")
        self.totalOver10Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # over 10s

        self.totalOver60Label = QLabel(f"Streams over 60 seconds: {totalOver60:,.0f}")
        self.totalOver60Label.setToolTip("How many of the total streams lasted for over 60 seconds")
        self.totalOver60Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # over 60s

        self.totalPercentLabel = QLabel(f"{totalPercent} of time spent listening to Spotify")
        self.totalPercentLabel.setToolTip("How much of the time period has been spent listening to Spotify")
        self.totalPercentLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # percentage

        self.averageDurLabel = QLabel(f"Average song duration: {totalAverage}")
        self.averageDurLabel.setToolTip("How long the streams played for on average (min:sec)")
        self.averageDurLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # average

        self.mainOverviewTopLayout.addWidget(self.totalTitleLabel)
        self.mainOverviewLayout.addWidget(self.totalPlaysLabel)
        self.mainOverviewLayout.addWidget(self.totalTimeLabel)
        self.mainOverviewLayout.addWidget(self.uniqueLabel)
        self.mainOverviewLayout.addWidget(self.totalOver10Label)
        self.mainOverviewLayout.addWidget(self.totalOver60Label)
        self.mainOverviewLayout.addWidget(self.totalPercentLabel)
        self.mainOverviewLayout.addWidget(self.averageDurLabel)
        # adds each widget to the layout

    ### Monthly ###

        monthlyData = self.additional["Monthly"]
        # grabs the nested dictionary for the monthly data

        monthStart = pd.Timestamp(monthlyData["Month Start"])
        # grabs the start of the month, turns back into timestamp
        monthEnd = pd.Timestamp(monthlyData["Month End"])
        # grabs the end of the month, turns back into timestamp
        monthPeriod = f"{monthStart.day}.{monthStart.month} - {monthEnd.day}.{monthEnd.month}"
        # forms a string for the date period

        monthPlaycount = int(monthlyData["Playcount"])
        # grabs the playcount (int)
        monthPlaytime = int(monthlyData["Playtime"])
        # grabs the playtime (int)
        monthPercent = str(monthlyData["Percent"])
        # grabs the percentage (str (2-decimal percentage)+%)

        monthOver10 = int(monthlyData["Over10"])
        # grabs the number of plays over 10 seconds (int)
        monthOver60 = int(monthlyData["Over60"])
        # grabs the number of plays over 60 seconds (int)
        monthAverage = str(monthlyData["Average"])
        # grabs the average track duration (MM:SS)

        monthUniqueTracks = int(monthlyData["Tracks"])
        monthUniqueArtists = int(monthlyData["Artists"])
        monthUniqueAlbums = int(monthlyData["Albums"])
        # grabs the unique track, artist and album counts

        self.monthTitleLabel = QLabel(f"{monthStart.strftime("%B")}'s Spotify statistics\n({monthPeriod})")
        self.monthTitleLabel.setStyleSheet("font-size: 20px; font-weight: bold; font-style: italic;")
        self.monthTitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title

        self.monthPlaysLabel = QLabel(f"Streams: {monthPlaycount:,.0f}")
        self.monthPlaysLabel.setToolTip(f"How many Spotify tracks were played over the course of {monthStart.strftime("%B")}")
        self.monthPlaysLabel.setStyleSheet("font-size: 16px; font-weight: bold; font-style: italic;")
        self.monthPlaysLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # plays

        self.monthTimeLabel = QLabel(f"Listening time: {(monthPlaytime / self.totalDivisor):,.0f} {self.totalFormat.lower()}")
        self.monthTimeLabel.setToolTip(f"How long you've spent listening to Spotify during the month of {monthStart.strftime("%B")}")
        self.monthTimeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # time

        self.monthUniqueLabel = QLabel(f"Tracks: {monthUniqueTracks:,.0f}, Artists: {monthUniqueArtists:,.0f}, Albums: {monthUniqueAlbums:,.0f}")
        self.monthUniqueLabel.setToolTip(f"How many unique tracks, artists and albums you've listened to during {monthPeriod}")
        self.monthUniqueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # unique

        self.monthOver10Label = QLabel(f"Streams over 10 seconds: {monthOver10:,.0f}")
        self.monthOver10Label.setToolTip("How many of the monthly streams lasted for over 10 seconds")
        self.monthOver10Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # over 10s

        self.monthOver60Label = QLabel(f"Streams over 10 seconds: {monthOver60:,.0f}")
        self.monthOver60Label.setToolTip("How many of the monthly streams lasted for over 60 seconds")
        self.monthOver60Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # over 60s

        self.monthPercentLabel = QLabel(f"{monthPercent} of time spent listening to Spotify")
        self.monthPercentLabel.setToolTip("How much of the time period has been spent listening to Spotify")
        self.monthPercentLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # percentage

        self.monthAvgDurLabel = QLabel(f"Average song duration: {monthAverage}")
        self.monthAvgDurLabel.setToolTip("How long the streams played for on average (min:sec)")
        self.monthAvgDurLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # average

        self.leftSideTopLayout.addWidget(self.monthTitleLabel)
        self.leftSideOverviewLayout.addWidget(self.monthPlaysLabel)
        self.leftSideOverviewLayout.addWidget(self.monthTimeLabel)
        self.leftSideOverviewLayout.addWidget(self.monthUniqueLabel)
        self.leftSideOverviewLayout.addWidget(self.monthOver10Label)
        self.leftSideOverviewLayout.addWidget(self.monthOver60Label)
        self.leftSideOverviewLayout.addWidget(self.monthPercentLabel)
        self.leftSideOverviewLayout.addWidget(self.monthAvgDurLabel)
        # adds each widget to the layout

    ### Yearly ###

        yearlyData = self.additional["Yearly"]
        # grabs the nested dictionary for the monthly data

        yearStart = pd.Timestamp(yearlyData["Year Start"])
        # grabs the start of the year, turns back into timestamp
        yearEnd = pd.Timestamp(yearlyData["Year End"])
        # grabs the end of the year, turns back into timestamp
        yearPeriod = f"{yearStart.day}.{yearStart.month}.{yearStart.year} - {yearEnd.day}.{yearEnd.month}.{yearEnd.year}"
        # forms a string for the date period

        yearPlaycount = int(yearlyData["Playcount"])
        # grabs the playcount (int)
        yearPlaytime = int(yearlyData["Playtime"])
        # grabs the playtime (int)
        yearPercent = str(yearlyData["Percent"])
        # grabs the percentage (str (2-decimal percentage)+%)

        yearOver10 = int(yearlyData["Over10"])
        # grabs the number of plays over 10 seconds (int)
        yearOver60 = int(yearlyData["Over60"])
        # grabs the number of plays over 60 seconds (int)
        yearAverage = str(yearlyData["Average"])
        # grabs the average track duration (MM:SS)

        yearUniqueTracks = int(yearlyData["Tracks"])
        yearUniqueArtists = int(yearlyData["Artists"])
        yearUniqueAlbums = int(yearlyData["Albums"])
        # grabs the unique track, artist and album counts

        self.yearTitleLabel = QLabel(f"{yearStart.year}'s Spotify statistics\n({yearPeriod})")
        self.yearTitleLabel.setStyleSheet("font-size: 20px; font-weight: bold; font-style: italic;")
        self.yearTitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title

        self.yearPlaysLabel = QLabel(f"Streams: {yearPlaycount:,.0f}")
        self.yearPlaysLabel.setToolTip(f"How many Spotify tracks were played over the course of {yearStart.year}")
        self.yearPlaysLabel.setStyleSheet("font-size: 16px; font-weight: bold; font-style: italic;")
        self.yearPlaysLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # plays

        self.yearTimeLabel = QLabel(f"Listening time: {(yearPlaytime / self.totalDivisor):,.0f} {self.totalFormat.lower()}")
        self.yearTimeLabel.setToolTip(f"How long you've spent listening to Spotify during {yearStart.year}")
        self.yearTimeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # time

        self.yearUniqueLabel = QLabel(f"Tracks: {yearUniqueTracks:,.0f}, Artists: {yearUniqueArtists:,.0f}, Albums: {yearUniqueAlbums:,.0f}")
        self.yearUniqueLabel.setToolTip(f"How many unique tracks, artists and albums you've listened to during {yearPeriod}")
        self.yearUniqueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # unique

        self.yearOver10Label = QLabel(f"Streams over 10 seconds: {yearOver10:,.0f}")
        self.yearOver10Label.setToolTip("How many of the yearly streams lasted for over 10 seconds")
        self.yearOver10Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # over 10s

        self.yearOver60Label = QLabel(f"Streams over 60 seconds: {yearOver60:,.0f}")
        self.yearOver60Label.setToolTip("How many of the yearly streams lasted for over 60 seconds")
        self.yearOver60Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # over 60s

        self.yearPercentLabel = QLabel(f"{yearPercent} of time spent listening to Spotify")
        self.yearPercentLabel.setToolTip("How much of the time period has been spent listening to Spotify")
        self.yearPercentLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # percentage

        self.yearAvgDurLabel = QLabel(f"Average song duration: {yearAverage}")
        self.yearAvgDurLabel.setToolTip("How long the streams played for on average (min:sec)")
        self.yearAvgDurLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # average

        self.rightSideTopLayout.addWidget(self.yearTitleLabel)
        self.rightSideOverviewLayout.addWidget(self.yearPlaysLabel)
        self.rightSideOverviewLayout.addWidget(self.yearTimeLabel)
        self.rightSideOverviewLayout.addWidget(self.yearUniqueLabel)
        self.rightSideOverviewLayout.addWidget(self.yearOver10Label)
        self.rightSideOverviewLayout.addWidget(self.yearOver60Label)
        self.rightSideOverviewLayout.addWidget(self.yearPercentLabel)
        self.rightSideOverviewLayout.addWidget(self.yearAvgDurLabel)
        # adds each widget to the layout

        print(f"{timestamper()} | Overview page created!\n")
        # user inform

        QTimer.singleShot(50, self.drawCharts)
        # calls the chart drawing function

### Chart Draw Selection ###

    def drawCharts(self):
        """Function to draw the relevant charts"""

        for name, dictionary in self.additional.items():
        # goes through every nested dictionary
            if name in ("Total", "Monthly", "Yearly"):
            # if the dictionary entry is for Monthly, Yearly or Total (they have a different logic, just sit in the same storage)
                continue
                # next
            if dictionary:
            # if that dictionary has data
                self.drawAdditionals(name, dictionary)
                # runs the additional chart drawer to draw that chart

        print(f"{timestamper()} | Drew data charts!\n")
        # user inform

        self.drawRankingCharts()
        # calls the next step (summary/ranking charts)

### Additional Charts ###

    def drawAdditionals(self, addChartName:str, nestedDict:dict[str, str | int | float]):
        """Function to draw additional dictionary-related charts"""

        addLabels = []
        # empty list for the actual labels 

        rawLabels = list(nestedDict.keys())
        # gets the names of the keys (key:value), uses them as (additional)labels
        addValues = list(nestedDict.values())
        # gets the values for each key, uses them as chart (additional)values

        if not addChartName == "Platform":
        # platform already has customised labels
            for label in rawLabels:
            # goes through every label in the raw list
                addLabels.append(str(label).capitalize())
                # capitalises the label, adds to final list (eg. "false" -> "False")
        else:
        # platform chart specifically
            addLabels = rawLabels
            # uses the list of raw labels as the final list

        if addChartName in ("Shuffle", "Skipped", "Offline"):
        # if the chart name is one of the above (they just store True/False)
            self.drawPieChart(addChartName, addLabels, addValues)
            # runs the pie chart drawer
        else:
        # chart name not one of those (they store very different names)
            self.drawBarChart(addChartName, addLabels, addValues)
            # runs the bar chart drawer

### Bar Chart ###

    def drawBarChart(self, chartName:str, labels:list[str], values:list[str | int | float]):
        """Function to draw a bar chart"""

        chartFigure = Figure(figsize=(10, 6), facecolor="#1E1E1E")
        # creates a matplotlib figure
        canvas = FigureCanvasQTAgg(chartFigure)
        # makes a canvas for figure to sit in

        ax = chartFigure.add_axes([0.09, 0.13, 0.85, 0.80], facecolor="#1E1E1E")
        # configures the chart axes (left, bottom, width, height)

        bars = ax.bar(labels, values, color="#1DB954")
        # makes a bar chart with the passed labels + values
        ax.set_title(chartName, color="white", pad=12)
        # adds a title (the name of the chart)

        ax.tick_params(axis="x", colors="white", labelrotation=22.5)
        ax.tick_params(axis="y", colors="white")
        # makes tick labels/ticks white, slants x-axis labels

        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        # formats the y-axis numbers with thousands-splitters

        for bar, value in zip(bars, values):
        # goes through every bar (label) in the chart + every value
            ax.text((bar.get_x() + bar.get_width() / 2), (bar.get_height() + 0.1), f"{value:,.0f}", ha="center", va="bottom", color="white")
            # sets the position of the labels above the bars, sets the value to match the bar's value

        for spine in ax.spines.values():
        # goes through every border (spine)
            spine.set_color("white")
            # makes it white

        ax.grid(axis="y", color="#555555", linestyle="-", linewidth=0.5, alpha=0.5)
        # sets the grid rules (horizontal grid)
        ax.set_axisbelow(True)
        # moves the grid *behind* the bars (visual clutter reduction)

        self.addChart(chartName, canvas, False)
        # calls the chart adder to make a new page for the chart

### Pie Chart ###

    def drawPieChart(self, chartName:str, labels:list[bool | str], values:list[int | float]):
        """Function to draw a pie chart"""

        chartFigure = Figure(figsize=(10, 6), facecolor="#1E1E1E")
        # creates a matplotlib figure with dark background
        canvas = FigureCanvasQTAgg(chartFigure)
        # makes a canvas for figure to sit in

        ax = chartFigure.add_axes([0.09, 0.13, 0.85, 0.80], facecolor="#1E1E1E")
        # configures the chart axes (left, bottom, width, height)

        pieColors = []
        # empty list of colors

        for label in labels:
        # goes through the passed labels
            if label is True or label == "True":
            # if the label is True (or "True" in string form)
                pieColors.append("#1DB954")
                # adds a green color to elements
            else:
            # not True/true string -> False
                pieColors.append("#E63946")
                # adds red

        ax.pie(values, labels=labels, colors=pieColors[:len(values)], autopct=lambda percentage: f"{percentage * sum(values) / 100:,.0f}",
                textprops={"color": "white"}, wedgeprops={"edgecolor": "#424242", "linewidth": 2})
        # makes the pie chart with colored sections and white text, displays the exact value of the slice 

        ax.set_title(chartName, color="white", pad=12)
        # adds a title (the name of the chart)

        self.addChart(chartName, canvas, False)
        # calls the chart adder to make a new page for the chart

### Ranking Charts ###

    def drawHBarChart(self, chartName:str, dataframe:pd.DataFrame, labelColumn:str, valueColumn:str):
        """Function to draw a horizontal bar chart"""

        labels = list(dataframe[labelColumn])
        # grabs the labels from the matching name of the dataframe
        values = list(dataframe[valueColumn])
        # grabs the values from the matching name of the dataframe

        hoverTextList = []
        # empty list of text to display on hover
        for _, row in dataframe.iterrows():
        # goes through the dataframe's rows
            rowData = {}
            # empty dict
            for column in dataframe.columns:
            # checks every column name
                if column not in (labelColumn, valueColumn):
                # if the column isn't the label or value column given as parameters
                    rowData[column] = row[column]
                    # adds that column's data to the rowData dictionary
            hoverTextList.append(rowData)
            # adds that row's data to the list of hover texts

        chartHeight = max(8, (len(labels) * 0.20))
        # calculates a "height" for the chart (ensures it doesn't go below 8 'inches', but can expand if there's a lot of data)

        chartFigure = Figure(figsize=(10, chartHeight), facecolor="#1E1E1E")
        # creates a matplotlib figure with dark background, sets the height dynamically
        canvas = FigureCanvasQTAgg(chartFigure)
        # makes a canvas for figure to sit in

        if valueColumn == "Total Time":
        # if the column is time (still unmodified, milliseconds)
            values = list(value / self.totalDivisor for value in values)
            # divides the values with the stored divisor (-> seconds/minutes/hours/days)
            if self.totalDivisor > 60000:
            # if the total divisor isn't seconds/minutes
                axisFormat = f"{{x:,.2f}} {self.totalFormat.lower()}"
                valueFormat = f"{{:,.2f}} {self.totalFormat.lower()}"
                # uses 2 decimal points
                rDelta = 1.125
                # sets the right-side delta multiplier to 1.15 (15%) (days and hours add a bit of string, but not a ton)
            else:
            # seconds/minutes
                axisFormat = f"{{x:,.0f}} {self.totalFormat.lower()}"
                valueFormat = f"{{:,.0f}} {self.totalFormat.lower()}"
                # uses no decimal point
                rDelta = 1.15
                # sets the right-side delta multiplier to 1.20 (20%) (minutes and seconds add a fair bit of string)
        else:
        # anything else (playcount)
            axisFormat = "{x:,.0f}"
            valueFormat = "{:,.0f}"
            # uses the standard thousands-splitter
            rDelta = 1.1
            # sets the right-side delta multiplier to 1.10 (10%)

        minValue = min(values)
        # gets the lowest value in the list of managed values (divided)
        maxValue = (max(values) * rDelta)
        # gets the highest value in the list of managed values (divided), adds some percentage to keep the right side from touching the values
        if minValue <= 0:
        # if the value is below 0
            xAxisMin = minValue
            # caps the x-axis start point to that value
        elif (((maxValue * 0.1) - minValue) > 0):
        # if the difference between max and min value is that large that 10% of max minus the min is still above 0
        # eg. max value of 5,000, min of 300 = 500 - 300 > 0, at that point displaying the full 300 is just a QoL necessity 
            xAxisMin = 0
            # caps at 0
        else:
        # value above 0
            xAxisMin = max(0, (minValue * 0.90))
            # stops the minimum going under 0

        ax = chartFigure.add_axes([0.10, 0.10, 0.85, 0.80], facecolor="#1E1E1E")
        # configures the chart axes (left, bottom, width, height)
        ax.set_xlim(left=xAxisMin, right=maxValue)
        # sets the x-axis limits (moves left closer, generally speaking, and right further)

        barPositions = range(len(values))
        # gets the total number of values, gets a range to pass as bar positions
        bars = ax.barh(barPositions, values, color="#1DB954")
        # makes a bar chart with the number of values + passed values (colors with Spotify green)

        gapPixels = 8
        # how many pixels apart the labels should be from the bars
        labelGap = ScaledTranslation((gapPixels / chartFigure.dpi), 0, chartFigure.dpi_scale_trans)
        # calculates an offset based on the chart's dots per inch and the pixel count

        if not chartName in ("Month Ranks", "Year Ranks"):
        # these charts have numberic labels (years) or they can't exceed 15 characters anyway ('September 2026' = 14)
            chartLabels = list(range(1, (len(labels) + 1)))
            # gets a list of numbers to use as ranks
        else:
        # month or year rank charts
            chartLabels = labels
            # uses the labels list as-is (eg. June, October 2021, 2017)

        ax.set_yticks(barPositions)
        # sets the y-axis ticks at the bars' positions
        ax.set_yticklabels(chartLabels)
        # sets the labels from the list of truncated labels

        chartFigure.text(0.5, 0.97, chartName, color="white")
        # adds a 'title' (avoids actual .set_title, to set the coordinates, given the chart expands vertically)

        ax.tick_params(axis="x", colors="white", labelrotation=22.5)
        ax.tick_params(axis="y", colors="white")
        # makes tick labels/ticks white, slants x-axis labels

        ax.grid(axis="x", color="#555555", linestyle="-", linewidth=0.5, alpha=0.5)
        # sets the grid rules (vertical grid)
        ax.set_axisbelow(True)
        # moves the grid *behind* the bars (visual clutter reduction)

        ax.invert_yaxis()
        # flips the y-axis (top -> bottom)

        ax.xaxis.set_major_formatter(StrMethodFormatter(axisFormat))
        # formats the x-axis numbers with thousands-splitters

        for bar, value in zip(bars, values):
        # goes through every bar (label) in the chart + every value
            ax.text((bar.get_width()), (bar.get_y() + bar.get_height() / 2), valueFormat.format(value), transform=(ax.transData + labelGap), ha="left", va="center", color="white")
            # sets the position of the labels above the bars, sets the value to match the bar's value

        for spine in ax.spines.values():
        # goes through every border (spine)
            spine.set_color("white")
            # makes it white

        canvasHeight = int(chartHeight * chartFigure.dpi)
        # gets the height the canvas "should" be (gets the assigned height, multiplies by (dots per inch) to get pixels, ideally)
        canvas.setMinimumHeight(canvasHeight)
        # tells the canvas to use that height as a *minimum*
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # ensures the canvas expands horizontally to fit, but doesn't surpass sizing vertically (since it's told what the minimum should be anyway)

        canvas.draw()
        # ensures the canvas is rendered (so that the positions are )
        tickLabels = ax.get_yticklabels()
        # gets a list of where the y-axis ticks live (label "hitboxes" so to speak)

        canvas.mpl_connect("motion_notify_event", lambda event: self.chartTextHoverer(event, bars, tickLabels, hoverTextList, labels, values, valueColumn, valueFormat, canvas))
        # when the canvas detects motion over it, it sends an event to the hover handler

        self.addChart(chartName, canvas, True)
        # calls the chart adder to make a new page for the chart

### Label Truncation ###

    def truncateChartLabel(self, label: str, maxLength: int) -> str:
        """Function to truncate (cut short) a track/artist/album label (string) if it exceeds some length"""

        # unused function - used to use this for rankings, but the visuals suffered, replaced with ranks instead of truncated labels
        # maybe in the future?

        if len(label) <= maxLength:
        # if the string is shorter than max allowed
            return label
            # returns as-is

        return label[:(maxLength - 3)] + "..."
        # otherwise, returns the label cut down to the (max - 3), adds ... to the end (to indicate it's been cut short)

### Value Formatting ###

    def formatChartValue(self, columnName: str, value: int | float) -> str:
        """Function to format a passed value based on column name"""

        if columnName == "Total Time":
        # if the column is total time 
            value = (value / self.totalDivisor)
            # divides the value by the class-level divisor
            if self.totalDivisor > 60000:
            # if the total divisor isn't seconds/minutes
                return f"{value:,.2f} {self.totalFormat.lower()}"
                # uses 2 decimal points
            return f"{value:,.0f} {self.totalFormat.lower()}"
            # uses no decimal point

        if isinstance(value, (int, float)):
        # not total time - playcount (ignores string values like artists and such)
            return f"{value:,.0f}"
            # returns a formatted value

        return str(value)
        # otherwise, returns a stringified value

### Hover Detection ###

    def chartTextHoverer(self, event: MouseEvent, barContainers: BarContainer, tickLabels: list[Text], hoverTextList: list[dict[str, Any]], labels: list[str], values: list[int | float], valueColumn: str, valueFormat: str, canvas: FigureCanvasQTAgg):
        """Function to display on-hover text fields for charts with additional info"""

        if event.x is None or event.y is None:
        # if the passed x/y coordinates are empty
            QToolTip.hideText()
            # hides the hover text field
            self.hoveredText = None
            # resets the hovered text (since none is hovered now)
            return
            # stops

        hoveredIndex = None
        # sets the temp value for the hovered item index to None
        
        for index, bar in enumerate(barContainers):
        # goes through all the horizontal bars (bar containers), gets their index and details (coordinates)
            contains, _ = bar.contains(event)
            # checks if the event coordinates are inside the bar container
            if contains:
            # if they are
                hoveredIndex = index
                # grabs the index value
                break
                # stops looping

        if hoveredIndex is None:
        # if there's not a hovered item (bar) yet

            canvasRenderer = canvas.get_renderer()
            # uses the canvas's renderer
            
            for index, tickLabel in enumerate(tickLabels):
            # goes through all the labels of the canvas, gets their index and details (coordinates)

                tickLocation = tickLabel.get_window_extent(renderer=canvasRenderer)
                # gets the window size (hitbox)

                if tickLocation.contains(event.x, event.y):
                # if the x and y coordinates overlap with the label
                    self.hoveredText = index
                    # sets the hovered text field to the current index
                    break
                    # stops looping

        if hoveredIndex is None:
        # if the bar check and the label check found nothing
            QToolTip.hideText()
            # hides the field
            self.hoveredText = None
            # resets the current hover class variable
            return
            # stops running function (nothing to do)

        self.hoveredText = hoveredIndex
        # stores the hovered text's index in the class variable 
        hoverData = hoverTextList[hoveredIndex]
        # gets the hover text data for the given index

        hoverFieldText = (
            f"<b>{labels[hoveredIndex]}</b><br>"
            f"Rank: {hoveredIndex + 1}<br>"
            f"<br>"
            f"{valueColumn}: "
            f"{valueFormat.format(values[hoveredIndex])}<br>"
        )
        # forms an HTML item to display on hover as a new text field (uses the passed parameters to grab the relevant data)

        for columnName, value in hoverData.items():
        # goes through the hover text data

            formattedValue = self.formatChartValue(columnName, value)
            # calls the chart value formatter to get the clean value (eg. "59395120" (total time, in ms) -> "989.91 minutes")
            hoverFieldText += f"{columnName}: {formattedValue}<br>"
            # adds that text to the hover field, too

        QToolTip.showText(QCursor.pos(), hoverFieldText, canvas)
        # displays the hover text field

### Ranking Chart Creator ###

    def drawRankingCharts(self):
        """Function to draw the relevant ranking charts"""

        self.rankingsPage = QWidget()
        # makes a page (widget) for the rankings view
        self.pageStack.addWidget(self.rankingsPage)
        # adds the page to the stack

        self.rankingStack = QStackedWidget()
        # creates a widget stack for the ranking charts (allows the ranking charts to sit inside the box, without having to render one per chart)

        self.rankingPageLayout = QGridLayout(self.rankingsPage)
        # makes a layout for the page
        self.rankingPageLayout.setContentsMargins(0, 0, 0, 0)
        # removes content margins
        self.rankingPageLayout.addWidget(self.rankingStack)
        # adds the ranking box inside the layout

        for sheetName, dataframe in self.excelSheets.items():
        # goes through every sheet + dataframe in the excelSheet dictionary {sheet : df}
            if sheetName not in ("Total Summary", "Monthly Summary", "Yearly Summary"):
            # these sheets work differently
                if not dataframe.empty:
                # if the dataframe has data
                    labelColumn = dataframe.columns[0]
                    # grabs the 0th column's name (track/artist/album/period)
                    if sheetName not in ("Month Ranks", "Year Ranks"):
                    # these sheets shouldn't be sorted by values (they're already sorted)
                        dataframe = dataframe.sort_values(by=self.sortColumn, ascending=False)
                        # ensures the dataframe contents are now sorted according to the sort column (playcount or time)
                    self.drawHBarChart(sheetName, dataframe, labelColumn, self.sortColumn)
                    # calls the chart drawer with the name of the sheet, the dataframe itself and the dataframe label/value column names

        rankChartList = list(self.rankingPages.keys())
        # gets all the rank chart names from the dictionary
        selectedChart = rankChartList[0]
        # grabs the 0th element
        rankChartList.remove(selectedChart)
        # removes that chart from the list

        self.dataframeDropdown.addItem(selectedChart)
        # adds the 0th chart
        self.dataframeDropdown.addItems(rankChartList)
        # adds all the available charts (grabs the names from the dictionary)

        self.dataframeDropdown.hide()
        # hides the secondary dropdown (since the overview page is the first to open)

        print(f"{timestamper()} | Drew ranking charts!\n")
        # user inform

        self.chartsDone()
        # calls the chart finaliser (sets up the pages + dropdown, shows window)

### Swap Ranking Charts ###

    def swapRankingChart(self):
        """Function to swap between the ranking charts"""

        selectedChart = self.dataframeDropdown.currentText()
        # grabs the currently selected chart from the dataframe dropdown
        selectedPage = self.rankingPages[selectedChart]
        # gets the page matching that chart from the dictionary
        selectedScroll = self.rankingScrolls[selectedChart]
        # gets the scroll area matching that chart from the dictionary

        self.rankingStack.setCurrentWidget(selectedPage)
        # sets the active widget to the selected chart
        selectedScroll.verticalScrollBar().setValue(0)
        # resets the scroll of that page to 0 (top)

### Add Charts ###

    def addChart(self, chartName:str, canvas:FigureCanvasQTAgg, ranking:bool=False):
        """Function to dynamically add a chart + layout page"""

        page = QWidget()
        # makes a new widget (page) for the chart

        pageMainLayout = QGridLayout(page)
        # makes a layout for the whole page (simple QGrid)
        pageBox = QGroupBox()
        # a box, literally, to house the data
        pageMainLayout.addWidget(pageBox)
        # adds the box to the center of the layout

        pageLayout = QVBoxLayout(pageBox)
        # makes a vertical-only layout inside the box
        pageLayout.setContentsMargins(0, 0, 0, 0)
        # removes margins inside the layout

        if ranking:
        # if the chart is to sit in the ranking chart page, not the main one
            scrollArea = QScrollArea()
            # makes a scroll area (quite literally an area you can scroll)
            scrollArea.setContentsMargins(0, 0, 0, 0)
            # sets the margins to 0 (no padding)

            scrollArea.setWidgetResizable(True)
            # stops the canvas from resizing itself out of the box

            scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            # disables the horizontal scroll bar
            scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            # sets the vertical scroll bar to appear when necessary

            scrollWidget = QWidget(scrollArea)
            # a widget to sit inside the scroll area
            scrollWidget.setStyleSheet("background-color: #1E1E1E;")
            # ensures it uses the correct coloring 

            scrollLayout = QVBoxLayout(scrollWidget)
            # a layout to sit in the scroll area (helps with the canvas spreading)
            scrollLayout.setContentsMargins(0, 0, 0, 0)
            # sets the margins to 0 (no padding)
            scrollLayout.addWidget(canvas)
            # adds the canvas to that layout

            scrollArea.setWidget(scrollWidget)
            # makes the canvas sit inside the scroll area
            pageLayout.addWidget(scrollArea)
            # adds the scroll area to the layout

            self.rankingStack.addWidget(page)
            # adds the new page to the stack

            self.rankingScrolls[chartName] = scrollArea
            # stores a dynamic reference to the scroll area in the scroll dictionary
            self.rankingPages[chartName] = page
            # stores a dynamic reference to the page in the page dictionary

        else:
        # not a ranking chart = main
            pageLayout.addWidget(canvas)
            # adds the passed canvas to the box layout

            self.pageStack.addWidget(page)
            # adds the new page to the stack
            self.pages[chartName] = page
            # stores a dynamic reference to the page in the page dictionary

### Swap Charts ###

    def swapChart(self):
        """Function to swap between the charts"""

        selectedChart = self.chartDropdown.currentText()
        # grabs the current text of the chart dropdown

        if selectedChart == "Rankings":
        # ranking chart page (contains sub-pages)
            selectedPage = self.rankingsPage
            # sets the page to the rankings page
            self.dataframeDropdown.show()
            # displays the secondary dropdown
        else:
        # not the rankings page
            self.dataframeDropdown.hide()
            # hides the secondary dropdown
            if selectedChart == "Overview":
            # if the 'chart' is the overview page
                selectedPage = self.overviewPage
                # sets the page to be the overview page
            else:
            # not overview = dynamic page
                selectedPage = self.pages[selectedChart]
                # grabs the page reference

        self.pageStack.setCurrentWidget(selectedPage)
        # sets the page stack widget to match the selected item

### Charts Done ###

    def chartsDone(self):
        """Function to complete the chart build stage and display the """

        self.activeCharts = []
        # a list of active charts

        for page in self.pages.keys():
        # goes through every chart draw in the charts dictionary
            self.activeCharts.append(page)
            # adds the chart to the list of active charts

        self.chartDropdown.addItem("Overview")
        # adds the overview page as the first (default) selection
        self.chartDropdown.addItem("Rankings")
        # adds the rankings page as the second selection (custom)
        self.chartDropdown.addItems(self.activeCharts)
        # adds all the actual chart names, too

        self.show()
        # once all the charts are drawn, shows the window 





### Stage 1: Raw JSON Processor ###

def StageOne(zipPath: str):
    """Stage 1: Zip file of .jsons -> one list"""
    global stageOneOutput
    # global -> local

    with zipfile.ZipFile(zipPath, "r") as dataFiles:
        # opens the zip file via formed path

        dataFileList = dataFiles.namelist()
        # grabs every file inside the .zip (includes some garbage)
        jsonNames = [file for file in dataFileList if file.endswith("json")]
        # goes through all the files in the list of data files, only grabs files that end in.json
        jsonNames.sort()
        # somewhat sorts the files

        print(f"\n{timestamper()} | Starting Stage 1: JSON processing\n")
        # user inform

        if dsiExport:
        # if the config option for DSI is on, uses a pre-set list
            removeableFields = ["platform", "conn_country", "ip_addr", "ip_addr_decrypted", "episode_name", "episode_show_name", "spotify_episode_uri",
                                "audiobook_title", "audiobook_uri", "audiobook_chapter_uri", "audiobook_chapter_title",
                                "reason_start", "reason_end", "shuffle", "skipped", "username", "offline", "user_agent_decrypted", "offline_timestamp", "incognito_mode"]
            # the list of fields DSI doesn't use at all

        else:
        # if the config option for DSI export isn't on
            removeableFields = [
                "conn_country", 
                "ip_addr", 
                "ip_addr_decrypted",
                "episode_name", 
                "episode_show_name", 
                "spotify_episode_uri"
                "audiobook_title", 
                "audiobook_uri", 
                "audiobook_chapter_uri", 
                "audiobook_chapter_title", 
                "offline_timestamp", 
                "username", 
                "user_agent_decrypted",
                "incognito_mode"
                ]
            # the base list of information to filter out (there is borderline no reason to keep any of these - audiobooks are deprecated and only show up on extremely old data)

            if not cfgPlatform:
                removeableFields.append("platform")
            if not cfgStartReason:
                removeableFields.append("reason_start")
            if not cfgEndReason:
                removeableFields.append("reason_end")
            if not cfgShuffle:
                removeableFields.append("shuffle")
            if not cfgSkipped:
                removeableFields.append("skipped")
            if not cfgOffline:
                removeableFields.append("offline")
            # adds all the unwanted optional fields to the list of removeable fields

        jsonLength = len(jsonNames)
        # stores the number of .json files
        printAt = 25
        # sets a checkpoint to print at (percentage)
        progress = 0
        # progress counter

        for jsonFile in jsonNames:
            # goes through json files one by one
            content = dataFiles.read(jsonFile)
            # reads the file
            jsonData = json.loads(content)
            # picks out the data from the read file

            for spotifyStream in jsonData:
            # goes through each individual stream in the loaded json file
                for unwantedField in removeableFields:
                # takes a field from the list of fields to get rid of
                    spotifyStream.pop(unwantedField, None)
                    # removes that field from each stream
                stageOneOutput.append(spotifyStream)
                # pushes the current stream's info into the output list

            progress += 1
            # adds 1 to counter every time a file is read
            percent = int((progress / jsonLength) * 100)
            # calculates the percentage of progress
            if percent >= printAt:
            # if the percent passes the next 25% print checkpoint
                print(f"{timestamper()} | Progress at: {printAt}%")
                # sends percentage progress to help visualise
                printAt += 25
                # adds 25 to the print requirement (eg. 25% -> 50% till next print)

        print(f"\n{timestamper()} | Stage 1 complete!\n{timestamper()} | Total Spotify streams: {len(stageOneOutput):,.0f}\n")
        # finishes work and checks if user wants to continue

        StageTwo()
        # runs the next stage





### Stage 2: Raw Output -> Formatted Data ###

def StageTwo():
    """Stage 2: Raw Stage 1 output list -> list of nicely formatted data"""
    global stageTwoOutput
    # global -> local

    print(f"\n{timestamper()} | Starting Stage 2: Data Formatting\n")
    # user inform

    for stream in stageOneOutput:
    # for every stream in the list of streams from stage 1

        streamTimestamp = stream.get("ts")
        # grabs the timestamp (default format is ISO (YYYY-MM-DDTHH:MM:SSZ))
        streamTempTS = datetime.datetime.fromisoformat(streamTimestamp)
        streamDateTS = streamTempTS.strftime("%Y-%m-%d")
        streamTimeTS = streamTempTS.strftime("%H:%M:%S")
        # timestamp-related stuff (splits into two, formats the stamp(s) better (Year-Month-Day + Hour:Minute:Second))

        streamPlatform = stream.get("platform")
        # gets the platform (if it exists)

        streamPlaytime = stream.get("ms_played")
        # gets the playtime of the stream

        streamName = stream.get("master_metadata_track_name")
        singleStreamArtist = stream.get("master_metadata_album_artist_name")
        singleStreamAlbum = stream.get("master_metadata_album_album_name")
        # gets the names of the track, artist and album

        streamURI = stream.get("spotify_track_uri")
        # gets the URI (identifier) of the track

        streamStartR = stream.get("reason_start")
        streamEndR = stream.get("reason_end")
        # gets the start and end reasons of the tracks

        streamShuffle = stream.get("shuffle")
        streamSkipped = stream.get("skipped")
        streamOffline = stream.get("offline")
        # grabs all the different user playback states
        
        stageTwoOutput.append({
            "Track": streamName,
            "Duration": streamPlaytime,
            "Date": streamDateTS,
            "Time": streamTimeTS,
            "Total Time": streamPlaytime,
            "Artist": singleStreamArtist,
            "Album": singleStreamAlbum,
            "Start Reason": streamStartR,
            "End Reason": streamEndR,
            "Shuffle": streamShuffle,
            "Skipped": streamSkipped,
            "Platform": streamPlatform,
            "URI": streamURI,
            "Offline": streamOffline
        })
        # appends the output list with a new dictionary containing the data for this stream
        
    print(f"\n{timestamper()} | Stage 2 complete!\n")
    # user inform

    StageThree()
    # runs the next stage





### Stage 3: Mathematician ###

def StageThreeHelper(fakeList: Any) -> pd.Series:
    """Helper function that takes a "list", drops "NaN" (unavailable) values, then turns into a dictionary"""

    return pd.Series(fakeList).dropna().value_counts().to_dict()
    # takes the passed list of elements, drops NaN/null/empty values, counts them and turns to a dict -> Series
    # eg. [Windows 10 Build XYZ, Android XYZ, Samsung XYZ, Windows 10 Build XYZ] -> {Windows 10 Build XYZ: 2, Android XYZ: 1, Samsung XYZ: 1}



def StageThree():
    """Stage 3: Formatted data -> grouped, calculated data"""
    global stageThreeData, stageThreeOutput
    # global -> local

    print(f"\n{timestamper()} | Starting Stage 3: Data Grouping\n")
    # user inform

    stageThreeData = pd.DataFrame(stageTwoOutput)
    # treats the list of dictionaries as a single dataframe

    if not dsiExport:
    # if DSI exporting isn't true, uses the "main" method of grouping
        stageThreeOutput = stageThreeData.groupby(["Track", "Artist", "Album"]).agg({"Duration": list, "Date": list, "Time": list, "Total Time": "sum", "Start Reason": StageThreeHelper, "End Reason": StageThreeHelper, "Shuffle": StageThreeHelper, "Skipped": StageThreeHelper, "Platform": StageThreeHelper, "URI": StageThreeHelper, "Offline": StageThreeHelper})
        # combines all occurances of a track that has the same name, artist and album into one multi-index - creates a dictionary for most pieces of info, except duration, which it sums up (as milliseconds)
        stageThreeOutput.insert(0, "Playcount", stageThreeOutput["Date"].str.len())
        # inserts a playcount column that counts the total plays of that track (counts the length of date strings for the track)

        stageThreeOutput.to_csv(finalCsvPath, index=True)
        # pushes the whole modified dataframe into a CSV file, now with Track, Artist and Album as multi-index 

        print(f"\n{timestamper()} | Stage 3 complete!\n")
        # user inform
        
        StageFour(True)
        # runs the next stage

    else:
    # if the config setting for DSI exporting is enabled
        dsiStageThreeOutput = stageThreeData.groupby(["Track"]).agg({"Artist": "first", "Album": "first", "Duration": list, "Date": list, "Time": list, "Total Time": "sum", "URI": lambda x: list(dict.fromkeys(x.dropna()))})
        # stores the csvData as a groupby of just the track (this is what DSI requires to function)
        dsiStageThreeOutput.insert(0, "Playcount", dsiStageThreeOutput["Date"].str.len())
        # inserts a playcount column that counts the total plays of that track (counts the length of date strings for the track)

        csvSeconds = float(dsiStageThreeOutput["Total Time"].sum() / 1000)
        # takes the total hours from the csv (turns total time for each track from milliseconds to (/1000) seconds to minutes (/60) to hours (/60)
        csvMinutes = float(csvSeconds / 60)
        # turns the second variable to minutes
        csvHours = float(csvMinutes / 60)
        # turns the minute variable to hours
        csvPlaycount = int(dsiStageThreeOutput["Playcount"].sum())
        # counts the total amount of playcount appearances
        csvAverageMin, csvAverageSec = divmod(int(csvSeconds / csvPlaycount), 60)
        # averages the total playtime across all tracks
        csvAverage = f"{int(csvAverageMin)}:{int(csvAverageSec):02d}"
        # turns the average into a string of m:ss

        top10TrackDF = dsiStageThreeOutput.nlargest(10, "Total Time")
        # grabs the 10 highest in the total time column
        top10Tracks = {}
        # empty dict to hold the top track data
        for _, row in top10TrackDF.iterrows():
        # goes through every row in the dataframe
            for uri in row["URI"]:
            # if there's more than 1 URI stored in the row (multi-URI tracks)
                top10Tracks[uri] = row["Total Time"]
                # stores that URI as the key of the dict, the total time as the value

        top10ArtistDF = stageThreeData.groupby("Artist").agg({"Total Time": "sum", "URI": lambda x: list(dict.fromkeys(x.dropna()))}).nlargest(10, "Total Time")
        # groups the original data by artists, adds up the total time and keeps the URIs intact, then gets the 10 highest
        top10Artists = {}
        # empty dict...
        for _, row in top10ArtistDF.iterrows():
        # goes through every row in the dataframe
            for uri in row["URI"]:
            # if there's more than...
                top10Artists[uri] = row["Total Time"]
                # stores that URI..

        top10AlbumDF = stageThreeData.groupby("Album").agg({"Total Time": "sum", "URI": lambda x: list(dict.fromkeys(x.dropna()))}).nlargest(10, "Total Time")
        # groups the original data by albums, adds up the total time and keeps the URIs intact, then gets the 10 highest
        top10Albums = {}
        # empty dict...
        for _, row in top10AlbumDF.iterrows():
        # goes through every row in the dataframe
            for uri in row["URI"]:
            # if there's more than...
                top10Albums[uri] = row["Total Time"]
                # stores that URI...

        uniqueTracks = len(stageThreeData["Track"].unique())
        # grabs the number of unique tracks
        uniqueArtists = len(stageThreeData["Artist"].unique())
        # grabs the number of unique artists
        uniqueAlbums = len(stageThreeData["Album"].unique())
        # grabs the number of unique albums

        hourlyPlays = (stageThreeData["Time"].str[:2].value_counts().sort_index()).to_dict()
        # gets the Time column from stage 2 (3 start), gets the first 2 letters (eg. *14*:32:41 or *02*:58:01), counts the values and sorts -> dictionary of {"00": somenumber, "01": someothernumber}

        dsiTimes = {
            "totalHours": csvHours,
            "totalMinutes": csvMinutes,
            "totalSeconds": csvSeconds,
            "totalPlays": csvPlaycount,
            "totalAverage": csvAverage,
            "topTracks": top10Tracks,
            "topArtists": top10Artists,
            "topAlbums": top10Albums,
            "hourlyPlays": hourlyPlays,
            "uniqueTracks": uniqueTracks,
            "uniqueArtists": uniqueArtists,
            "uniqueAlbums": uniqueAlbums,
            "timestamp": time.time()
        }
        # constructs a dictionary of data for DSI to use

        with open(dsiTotalTimePath, "w", encoding="utf-8") as times:
        # opens totalTimes.json
            json.dump(dsiTimes, times, indent=3)
            # pushes the times dictionary to the file

        dsiStageThreeOutput = dsiStageThreeOutput.explode("URI")
        # "explodes" the dataframe (takes all the tracks with multiple URIs and splits them into their own rows with identical data across the track's URIs)
        dsiStageThreeOutput.set_index("URI", inplace=True)
        # sets the index to URI
        dsiStageThreeOutput.to_csv(dsiCsvPath, index=True)
        # pushes the whole modified dataframe into a CSV file, now with URI as index

        print(f"\n{timestamper()} | Stage 3 complete!\n\n{timestamper()} | DSI files exported to:\n{timestamper()} | '{dsiCsvPath}' and '{dsiTotalTimePath}'")
        # user inform





### Stage 4: Summary ###

def StageFourListHelper(data: pd.DataFrame, columnName: str, divisor: int) -> list:
    """Helper function that takes passed parameters and returns a list of strings used for summarising (tracks, albums, artists)"""

    results = []
    # list of resulting strings (empty at start)

    for num, (_, row) in enumerate(data.iterrows(), start=1):
    # goes through every row in the passed dataframe

        artistString = None
        # empty string placeholder (may not get used)

        playcountString = f"Played {row['Playcount']:,.0f} times"
        # forms a string of how many times the item has been played
        playtimeString = f"Played for {row['Total Time'] / divisor:,.1f} {topTimeFormat.lower()}"
        # forms a string of how long the item has been played for

        artistString = f"\n{row['Artist']}" if columnName in ("Track", "Album") else ""
        # for column and album dataframes, adds the artist on a newline

        if topSelectionType == "Plays":
        # if the selected ranking type is Play(count)
            detailString = f"{playcountString}\n{playtimeString}"
            # string with playcount first
        else:
        # if the selected ranking type is Time
            detailString = f"{playtimeString}\n{playcountString}"
            # string with playtime first

        results.append(
            f"{row[columnName]}\n"
            # eg. #2: Diamonds & Dancefloors
            f"{detailString}"
            # eg. Played 6,322 times \n Played for 963,430 minutes
            f"{artistString}"
            # eg. Ava Max (only gets added for albums and tracks, artists don't need that clarification)
        )
        # adds the formed string to the list of strings

    return results
    # returns the list of strings



def StageFourDateHelper(data: pd.DataFrame, timePeriod: str, columnName: str, count: int, divisor: int) -> list:
    """Helper function that takes passed parameters and returns a list of date-based durations (months/years)"""

    results = []
    # list of resulting strings (empty at start)

    dateData = (data.resample(timePeriod, on="Date").agg({"Duration": "sum", "Date": "count"}).rename(columns={"Date": "Playcount", "Duration": "Total Time"}))
    # resamples the passed date based on the passed period 

    if columnName == "Total Time":
    # if using time-based ranking
        topDates = dateData.nlargest(count, "Total Time")
        # gets the top x dates with the highest playtimes
    else:
    # using count-based ranking
        topDates = dateData.nlargest(count, "Playcount")
        # gets the top x dates with the highest playcounts


    for num, (date, row) in enumerate(topDates.iterrows(), start=1):
    # goes through every row in the dataframe, grabs the date and row data

        playcountString = f"Played {row['Playcount']:,.0f} songs"
        # forms a string of how many times the item has been played
        playtimeString = f"Played for {row['Total Time'] / divisor:,.1f} {topTimeFormat.lower()}"
        # forms a string of how long the item has been played for

        if topSelectionType == "Plays":
        # if the selected ranking type is Play(count)
            detailString = f"{playcountString}\n{playtimeString}"
            # string with playcount first
        else:
        # if the selected ranking type is Time
            detailString = f"{playtimeString}\n{playcountString}"
            # string with playtime first

        if timePeriod == "YS":
        # if the called period is Year Start
            dateString = date.strftime("%Y")
            # formats the date to just year (eg. 2015 or 2026)
        else:
        # called period not Year -> Month Start
            dateString = date.strftime("%B %Y")
            # formats the month and year (since this only accepts individual month calls) -> (eg. June 2025 or September 2017)

        results.append(
            f"{dateString}\n"
            # eg. #2: June 2021 \n Played 6,322 times \n Played for 963,430 minutes
            f"{detailString}"
        )
        # adds the formed string to the list of strings

    return results
    # returns the list of strings



def StageFourDictHelper(series: pd.Series, normalise: bool=False) -> dict:
    """Function to help count dictionary totals"""
    total = Counter()
    # starts a counting total

    for cell in series.dropna():
    # goes through every cell of the series (drops empty cells)
        if not isinstance(cell, dict):
        # if the cell  isn't a dictionary
            continue
            # moves to next
        
        for keyName, count in cell.items():
        # gets the name of the key and the count of the key (eg. the platform cell may contain {"Windows 10 Build...": 593, "Android 11 OS...": 53})
            if normalise:
            # if calling to normalise (only the platform cells need this)
                keyName = StageFourPlatformHelper(keyName)
                # normalises (eg. "Windows 10 Build 19403.53" -> Windows)
            total[keyName] += count
            # adds the found count to that key's entry in the total

    return dict(total)
    # turns the counter into a dictionary, returns



def StageFourPlatformHelper(platform: str) -> str:
    """Function to normalise platform names"""

    platform = platform.lower()
    # ensures the string is lowercase (easier matches)

    if "chrome" in platform:
    # if the platform has "chrome"
        platform = "Chrome"
        # uses Chrome as platform name (rather than something like "web_player;chrome XY.Z")
    elif "firefox" in platform:
        platform = "Firefox"
        # uses Firefox as platform name
    elif "edge" in platform:
    # if the platform has "edge"
        platform = "Edge"
        # uses Edge as platform name
    elif "opera" in platform:
    # if the platform has "opera"
        platform = "Opera"
        # uses Opera as platform name
    elif "safari" in platform:
    # if the platform has "safari"
        platform = "Safari"
        # uses Safari as platform name
    elif "windows" in platform:
    # if the platform has "windows"
        platform = "Windows"
        # uses Windows as platform name (rather than something like "Windows 10 (10.0.19043; x64)")
    elif "linux" in platform:
    # if the platform has "linux"
        platform = "Linux"
        # uses Linux as platform name (rather than something like "Linux-bazite-10.53")
    elif "android" in platform:
    # if the platform has "android"
        platform = "Android"
        # uses Android as platform name (rather than something like "Android OS 11 API 30 (<brandname>, <model>)")
    elif any(x in platform for x in ["playstation", "ps4", "ps5"]):
    # if the platform has any playstation-related name
        platform = "PlayStation"
        # uses PlayStation as platform name
    elif "xbox" in platform:
    # if the platform has "xbox"
        platform = "XBOX"
        # uses XBOX as platform name
    elif "ios" in platform:
    # if the platform has "ios"
        platform = "iOS"
        # uses iOS as platform name (rather than something like "iOS 9.3.1 (iPhone<model>)")
    elif any(x in platform for x in ["os x", "mac os", "macos"]):
    # if any of the Mac OS naming schemes are in the platform name
        platform = "Mac OS"
        # uses Mac OS as platform name
    
    else:
    # no obvious match
        platform = platform.split(" ", 1)[0].capitalize()
        # splits the name by first space, keeps only the first part (helps with random names like TVs, dedicated players, etc)

    return platform
    # returns the normalised platform name



def StageFour(liveData: bool):
    """Stage 4: Summary function"""
    global excelSheets, extraInfoDict
    global topTrackCount, topArtistCount, topAlbumCount, topYearCount, topMonthCount
    # global -> local

    if liveData:
    # live data means "program ran through stages 1-3 prior and has data in variables" vs reading from file
        stageFourInitial = stageThreeOutput.reset_index()
        # grabs the variable data instead
        print(f"\n{timestamper()} | Starting Stage 4: Summary (via variable)\n")
        # user inform
    else:
    # starting from this stage
        stageFourInitial = pd.read_csv(finalCsvPath)
        # opens the finalised Stage 3 CSV file
        literalColumns = ["Date", "Duration", "Platform", "Start Reason", "End Reason", "Shuffle", "Skipped", "Offline"]
        # colums of the dataframe that should have literal evaluation applied (when saving the file, they get turned into strings, eg. "[list, of, elements]" rather than storing the list on its own)
        for column in literalColumns:
        # goes through every column in the list
            if column in stageFourInitial.columns:
            # if that column exists in the dataframe's columns
                stageFourInitial[column] = stageFourInitial[column].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else ({} if column not in ["Date", "Duration"] else []))
                # stores it again as a literal evaluation version (removes string markers (quotes)), if there's data (otherwise stores an empty dict or list)
        print(f"\n{timestamper()} | Starting Stage 4: Summary (via file)\n")
        # user inform

### Time Divisor ###

    if topTimeFormat == "Seconds":
    # if selected time format is seconds
        timeDivisor = 1000
        # sets the divider to 1,000 (ms -> seconds = 1,000 : 1)
    elif topTimeFormat == "Minutes":
    # if selected time format is minutes
        timeDivisor = 60000
        # sets the divider to 60,000 (ms -> minutes = 60,000 : 1)
    elif topTimeFormat == "Hours":
    # if selected time format is hours
        timeDivisor = 3600000
        # sets the divider to 3,600,000 (ms -> hours = 3,600,000 : 1)
    else:
    # selected time must be days
        timeDivisor = 86400000
        # sets the divider to 86,400,000 (ms -> days = 86,400,000 : 1)

### Top Selection ###
    
    if topSelectionType == "Plays":
    # if the selected method is to get the songs by playcount
        sortColumn = "Playcount"
        # uses the playcount as the column to rank with
    else:
    # if not playcount -> time 
        sortColumn = "Total Time"
        # uses the total time as the column to rank with

### Top Lists ###

    topTrackList = []
    topArtistList = []
    topAlbumList = []
    topMonthList = []
    topYearList = []
    # empty lists of the top items (lists of strings)

### Top Dataframes (Raw) ###

    topTracks = pd.DataFrame()
    topArtists = pd.DataFrame()
    topAlbums = pd.DataFrame()
    # overall top details

    topMonthTracks = pd.DataFrame()
    topMonthArtists = pd.DataFrame()
    topMonthAlbums = pd.DataFrame()
    # monthly top details

    topYearTracks = pd.DataFrame()
    topYearArtists = pd.DataFrame()
    topYearAlbums = pd.DataFrame()
    # yearly top details

### Date Manipulation ###

    stageFourDateFrame = stageFourInitial.copy()
    # creates a separate dataframe form the existing one (just because the DATE FRAME (haha, 12-hour coding sesh type joke) gets tweaked a lot)

    stageFourDateFrame = stageFourDateFrame.explode(["Date", "Duration"])
    # turns into a list of songs "exploded" by the dates and durations

    stageFourDateFrame["Date"] = pd.to_datetime(stageFourDateFrame["Date"])
    # ensures the dataframe now uses actual datetime format for the "date" column
    stageFourDateFrame["Duration"] = pd.to_numeric(stageFourDateFrame["Duration"])
    # ensures the dataframe now uses numbers for durations (shouldn't lead to "object" type errors)

    earliestDate = stageFourDateFrame["Date"].min().strftime("%B %d, %Y").replace(" 0", " ")
    # gets the "lowest" (earliest) date from the megalist of dates
    latestDate = stageFourDateFrame["Date"].max().strftime("%B %d, %Y").replace(" 0", " ")
    # gets the "highest" (latest) date from the megalist of dates

    print(f"{timestamper()} | Streamed dates range from {earliestDate} to {latestDate}")
    # user inform

### Top Tracks ###

    if topTrackCount >= 1:
    # if the selected number is now more than one (ensures user wants to get top tracks)

        if topTrackCount > 100:
        # if the selected number of top tracks exceeds 100
            topTrackCount = 100
            # caps at 100

        stageFourTrackData = (stageFourInitial[["Track", "Playcount", "Total Time", "Artist"]].groupby("Track").agg({"Total Time": "sum", "Playcount": "sum", "Artist": lambda x: ", ".join(x.unique())})).reset_index()
        # grabs the relevant information for the tracks

        topTracks = stageFourTrackData.nlargest(topTrackCount, sortColumn)
        # uses the user-configured number of top tracks and the predetermined column to sort by

        topTrackList = StageFourListHelper(topTracks, "Track", timeDivisor)
        # calls the helper function to get the list of top tracks

        print(f"{timestamper()} | Done grabbing top {topTrackCount} tracks!\n")
        # user inform

### Top Artists ###

    if topArtistCount >= 1:
    # if the selected number is now more than one (ensures user wants to get top artists)

        if topArtistCount > 100:
        # if the selected number of top artists exceeds 100
            topArtistCount = 100
            # caps at 100

        stageFourArtistData = (stageFourInitial[["Artist", "Total Time", "Playcount"]].groupby("Artist").agg({"Total Time": "sum", "Playcount": "sum"})).reset_index()
        # aggregates the data for artists 

        topArtists = stageFourArtistData.nlargest(topArtistCount, sortColumn)
        # gets the top artists from the dataframe

        topArtistList = StageFourListHelper(topArtists, "Artist", timeDivisor)
        # calls the helper function to get the list of top artists

        print(f"{timestamper()} | Done grabbing top {topArtistCount} artists!\n")
        # user inform

### Top Albums ###

    if topAlbumCount >= 1:
    # if the selected number is now more than one (ensures user wants to get top albums)

        if topAlbumCount > 100:
        # if the selected number of top albums exceeds 100
            topAlbumCount = 100
            # caps at 100

        stageFourAlbumData = (stageFourInitial[["Album", "Total Time", "Playcount", "Artist"]].groupby("Album").agg({"Total Time": "sum", "Playcount": "sum", "Artist": "first"})).reset_index()
        # aggregates the data for albums

        topAlbums = stageFourAlbumData.nlargest(topAlbumCount, sortColumn)
        # gets the top albums from the dataframe

        topAlbumList = StageFourListHelper(topAlbums, "Album", timeDivisor)
        # calls the helper function to get the list of top albums

        print(f"{timestamper()} | Done grabbing top {topAlbumCount} albums!\n")
        # user inform

### Top Months ###

    if topMonthCount >= 1:
    # ensures there's at least one month to check the top list for

        if individualMonths:
        # if the config option is on (counts each month of each year as its own entity)
            topMonthList = StageFourDateHelper(stageFourDateFrame, "MS", sortColumn, topMonthCount, timeDivisor)
            # gets the list of the highest months
            if topMonthCount > len(topMonthList):
            # if there's more requested months than there are in data
                topMonthCount = len(topMonthList)
                # sets to match (visual QoL only)
        else:
        # if the config option isn't on (each month is shared (June of 2025 counts toward the same as June of 2026))
            if topMonthCount > 12:
            # since there's only 12 total months
                topMonthCount = 12
                # caps the months at 12, if the number is over it 

            sharedMonthData = (stageFourDateFrame.groupby(stageFourDateFrame["Date"].dt.month).agg({"Duration": "sum", "Date": "count"}).rename(columns={"Duration": "Total Time", "Date": "Playcount"}))
            # aggregates the data by months (June of all years -> June)
            sharedMonthData.index.name = "Month"
            # renames the index from Date to Month (beacuse it's just a month number at this point, not a date)

            topMonths = sharedMonthData.nlargest(topMonthCount, sortColumn)
            # grabs the x most listened to months (sortColumn = playtime or count)
            topMonthList = []
            # empty list to hold data

            for num, (month, row) in enumerate(topMonths.iterrows(), start=1):
            # goes through every row, grabs the month
                playcountString = f"Played {row['Playcount']:,.0f} times"
                # forms a string of how many times the item has been played
                playtimeString = f"Played for {row['Total Time'] / timeDivisor:,.1f} {topTimeFormat.lower()}"
                # forms a string of how long the item has been played for

                if topSelectionType == "Plays":
                # if the selected ranking type is Play(count)
                    detailString = f"{playcountString}\n{playtimeString}"
                    # string with playcount first
                else:
                # if the selected ranking type is Time
                    detailString = f"{playtimeString}\n{playcountString}"
                    # string with playtime first

                monthName = pd.Timestamp(2000, int(month), 1).strftime("%B")
                # reformats the month to use actual datetime format (rather than "03" -> March)

                topMonthList.append(
                    f"{monthName}\n"
                    # eg. June \n Played 6,322 times \n Played for 963,430 minutes
                    f"{detailString}"
                )
                # adds the formed string to the list of strings
            
        print(f"{timestamper()} | Done grabbing top {topMonthCount} months!\n")
        # user inform

### Top Years ###

    if topYearCount >= 1:
    # if there's at least 1 year requested for

        topYearList = StageFourDateHelper(stageFourDateFrame, "YS", sortColumn, topYearCount, timeDivisor)
        # gets the list of the highest years

        if topYearCount > len(topYearList):
        # if there's more requested years than there are in data
            topYearCount = len(topYearList)
            # sets to match (visual QoL only)

        print(f"{timestamper()} | Done grabbing top {topYearCount} years!\n")
        # user inform

### General Info ###

    print(f"{timestamper()} | Calculating summary numbers\n")
    # user inform

    startStamp = pd.Timestamp(stageFourDateFrame["Date"].min())
    endStamp = pd.Timestamp(stageFourDateFrame["Date"].max())
    # start and end timestamps 

    totalPlays = len(stageFourDateFrame)
    # adds up all the playcounts
    totalTimeMs = int(stageFourDateFrame["Duration"].sum())
    # adds up all the total times per track (in milliseconds)
    totalTime = (totalTimeMs / timeDivisor)
    # divides the whole thing by the user-configured time

    averageDurationMin, averageDurationSec = divmod(int((totalTimeMs / totalPlays) / 1000), 60)
    # divides the total milliseconds with the total playcount, then divides with 1000 -> seconds
    totalPlaysOver10 = int((stageFourDateFrame["Duration"] > 10000).sum())
    # gets the total number of plays that lasted over 10 seconds
    totalPlaysOver60 = int((stageFourDateFrame["Duration"] > 60000).sum())
    # gets the total number of plays that lasted over 60 seconds

    timeSpent = (endStamp - startStamp).total_seconds()
    # gets the total number of seconds since the first stream
    totalPlayPercent = (((totalTimeMs / 1000) / timeSpent) * 100)
    # calculates how much of the history has been spent listening to Spotify (in seconds)
    totalPlayPercent = f"{totalPlayPercent:,.2f}%" if totalPlayPercent < 100 else "~100%"
    # if the percentage is <100, uses 2 decimals, if it's 100 (or capped at 100), uses 100%

    uniqueTracks = len(stageFourInitial["Track"].unique())
    # grabs the number of unique tracks
    uniqueArtists = len(stageFourInitial["Artist"].unique())
    # grabs the number of unique artists
    uniqueAlbums = len(stageFourInitial["Album"].unique())
    # grabs the number of unique albums

    print(
        f"{timestamper()} | Total song plays: {totalPlays:,.0f}\n"
        # total number of song plays (this is different from total streams because of videos and audiobooks/podcasts)
        f"{timestamper()} | Total time spent listening: {totalTime:,.0f} {topTimeFormat.lower()}\n"
        # gives the total time in the format dictated by topTimeFormat (eg. hours, seconds, minutes, days)
        f"{timestamper()} | Average song duration: {int(averageDurationMin)}:{int(averageDurationSec):02d}\n"
        # gets the average duration from above, reconstructs it as minutes:seconds (seconds are zero-padded (eg. 3:00 vs 3:0))
        f"{timestamper()} | Total plays over 10 seconds: {totalPlaysOver10:,.0f}\n"
        # total number of song plays that played for over 10 seconds (no skip or cut short)
        f"{timestamper()} | Total plays over 60 seconds: {totalPlaysOver60:,.0f}\n"
        # total number of song plays that played for over a minute
    )
    # user info package

    totalData = {
        "Start": startStamp.isoformat(),
        "End": endStamp.isoformat(),
        "Playcount": totalPlays,
        "Playtime": totalTimeMs,
        "Over10": totalPlaysOver10,
        "Over60": totalPlaysOver60,
        "Average": f"{int(averageDurationMin)}:{int(averageDurationSec):02d}",
        "Percent": totalPlayPercent,
        "Divisor": timeDivisor,
        "Format": topTimeFormat,
        "Individual Months": individualMonths,
        "Tracks": uniqueTracks,
        "Artists": uniqueArtists,
        "Albums": uniqueAlbums
    }
    # forms a dictionary of generally useful information

    time.sleep(3)
    # waits 3 seconds to allow quick glance at numbers

### Time-Based Data ###

    lastDataDate = pd.Timestamp((stageFourDateFrame["Date"].max()))
    # gets the max date found in the data (turns into a pd.Timestamp object)

    latestMonth = lastDataDate.to_period("M")
    # grabs the last month found in the data
    latestMonthStart = latestMonth.start_time
    # gets the day the month started
    latestMonthEnd = latestMonth.end_time
    # gets the day the month ended (or ends)

    latestYear = lastDataDate.to_period("Y")
    # grabs the last year found in the data
    latestYearStart = latestYear.start_time
    # gets the day the year started
    latestYearEnd = latestYear.end_time
    # gets the day the month ended (or ends)


    # should probably have a safeguard that checks that there *is* data for the previous x (mo/y) before allowing the program to try to access those

    if useFullPeriod == "Full":
    # if the option to use the full date periods only is enabled
        if lastDataDate.date() < latestMonthEnd.date():
        # if the data-end-date isn't when the month ends (eg. Sept 29th vs Sept 31st)
            currentMonth = (latestMonth - 1)
            # subtracts one month from the latest (uses last month's data)
        else:
        # if the data-end-date does match (eg. Feb 28th vs Feb 28th)
            currentMonth = latestMonth
            # uses the latest month

        if lastDataDate.date() < latestYearEnd.date():
        # if the data-end-date isn't when the year ends
            currentYear = (latestYear - 1)
            # subtracts one year from the latest (uses last year's data)
        else:
        # if the data-end-date does match the year end
            currentYear = latestYear
            # uses the latest year
    elif useFullPeriod == "Current":
    # option is set to current month, regardless of progress
        currentMonth = latestMonth
        # gets the latest month of data
        currentYear = latestYear
        # gets the latest year of data
    else:
    # option is set to a percentage, need to check the date to get smarter stats
        monthProgress = ((lastDataDate - latestMonthStart) / (latestMonthEnd - latestMonthStart))
        # gets the progress of the month (how far along is the data)
        yearProgress = ((lastDataDate - latestYearStart) / (latestYearEnd - latestYearStart))
        # gets the progress of the year (how far along is the data)

        try:
        # sticks in a try/except check (converting strings to int is always dangerous)
            threshold = (int(useFullPeriod.replace("%", "")) / 100)
            # removes the percentage mark, converts to integer -> turns into percentage (/100)
            # options are: 33%, 50%, 66%, 75%, 90%
        except:
        # if the conversion fails (prevents crash)
            threshold = 0.66
            # sets a manual override threshold of 66%

        if monthProgress >= threshold:
        # if the month has progressed past the threshold
            currentMonth = latestMonth
            # uses the latest data
        else:
        # if the month isn't past the threshold
            currentMonth = (latestMonth - 1)
            # subtracts one month from the latest (uses last month's data)

        if yearProgress >= threshold:
        # if the year has progressed past the threshold
            currentYear = latestYear
            # uses the latest data
        else:
        # if the year isn't past the threshold
            currentYear = (latestYear - 1)
            # uses last year's data

    if not stageFourDateFrame["Date"].dt.to_period("M").eq(currentMonth).any():
    # double-check after selection, checks if the current month has *some* data in the dataFrame
        currentMonthVerbose = currentMonth.strftime("%B")
        # gets the verbose name of the month (10 -> October)
        latestMonthVerbose = latestMonth.strftime("%B")
        # gets the verbose name of the month (6 -> June)
        print(f"{timestamper()} | No data found for {currentMonthVerbose}, falling back to {latestMonthVerbose}!\n")
        # user inform on error -> change
        currentMonth = latestMonth
        # uses the latest month instead
    
    if not stageFourDateFrame["Date"].dt.to_period("Y").eq(currentYear).any():
    # double-check after selection, checks if the current year has *some* data in the dataFrame
        print(f"{timestamper()} | No data found for {currentYear.year}, falling back to {latestYear.year}!\n")
        # user inform on error -> change
        currentYear = latestYear
        # uses the latest year instead

### Monthly Data ###

    monthStart = currentMonth.to_timestamp()
    monthEnd = (monthStart + pd.DateOffset(months=1))
    # gets the start and endpoints of the pd timestamp periods (eg. Aug 1st - Aug 19th (or the full month, if not at the halfway of the month yet))

    monthData = stageFourDateFrame[(stageFourDateFrame["Date"] >= monthStart) & (stageFourDateFrame["Date"] < monthEnd)]
    # grabs all the data between the start/end points for the month
    monthPlaycount = len(monthData)
    monthPlaytime = int(monthData["Duration"].sum())
    # gets the play count and time for the month

    monthSummary = pd.DataFrame()
    # a dataframe for the month's formatted data

    if topHistoricalCount >= 1:
    # if the summary top list option is at least 1

        monthTrackData = (monthData.groupby("Track").agg({"Duration": "sum", "Date": "count", "Artist": lambda x: ", ".join(x.unique())}).rename(columns={"Duration": "Total Time", "Date": "Playcount"})).reset_index()
        # gets the track data for the month
        topMonthTracks = monthTrackData.nlargest(topHistoricalCount, sortColumn)
        # gets the x highest tracks of the month
        topMonthTrackList = StageFourListHelper(topMonthTracks, "Track", timeDivisor)
        # calls the helper to get the list of tracks + details

        monthArtistData = (monthData.groupby("Artist").agg({"Duration": "sum", "Date": "count"}).rename(columns={"Duration": "Total Time", "Date": "Playcount"})).reset_index()
        # gets the artist data for the month
        topMonthArtists = monthArtistData.nlargest(topHistoricalCount, sortColumn)
        # gets the x highest artists of the month
        topMonthArtistList = StageFourListHelper(topMonthArtists, "Artist", timeDivisor)
        # calls the helper to get the list of artists + details

        monthAlbumData = (monthData.groupby("Album").agg({"Duration": "sum", "Date": "count", "Artist": "first"}).rename(columns={"Duration": "Total Time", "Date": "Playcount"})).reset_index()
        # gets the album data for the month
        topMonthAlbums = monthAlbumData.nlargest(topHistoricalCount, sortColumn)
        # gets the x highest albums of the month
        topMonthAlbumList = StageFourListHelper(topMonthAlbums, "Album", timeDivisor)
        # calls the helper to get the list of albums + details

        monthLists = {
            "Track": topMonthTrackList,
            "Artist": topMonthArtistList,
            "Album": topMonthAlbumList
        }
        # a dictionary with references between column names and lists

        highestMonthRank = max((len(topList) for topList in monthLists.values()), default=0)
        # goes through all the lists of top x, gets the longest length
        monthSummary["Rank"] = range(1, (highestMonthRank + 1))
        # makes a Rank column that ranges from 1 to X+1 (since len(list) is one-off)

        for x in monthLists.keys():
        # goes through the dictionary's keys (item names/strings)
            if len(monthLists[x]) > 0:
            # if the value of the matching list has at least 1 item (len > 0)
                monthSummary[x] = pd.Series(monthLists[x])
                # adds a column of x (track, album, artist, year, month...) and enters the values of that matching list (wraps in a Series to allow empty values to be added)
                # this is because you can have up to however many of eg. tracks (let's just say 100), but not necessarily as many artists (maybe 15)
                # without the pd.Series, the dataframe expects 100 values per column, since that's how big Rank is, but artists now only has 15 -> valueError, the pd.Series just fills with NaN
    
    monthSpentEnd = min(lastDataDate, monthEnd)
    # gets the earlier of the two - the last data stamp or the end of the month (if using incomplete data, lastDataDate < monthEnd, if using complete data, lastDataDate > monthEnd)
    monthSpent = (monthSpentEnd - monthStart).total_seconds()
    # calculates how many seconds the month has already burned through

    monthPlayPercent = (((monthPlaytime / 1000) / monthSpent) * 100)
    # calculates how much of the selected month has been spent listening to Spotify (in seconds)
    monthPlayPercent = f"{monthPlayPercent:,.2f}%" if monthPlayPercent < 100 else "~100%"
    # if the percentage is <100, uses 2 decimals, if it's 100 (or capped at 100), uses 100%

    monthAvgDurMin, monthAvgDurSec = divmod(int((monthPlaytime / monthPlaycount) / 1000), 60)
    # divides the milliseconds with the playcount, then divides with 1000 -> seconds
    monthPlaysOver10 = int((monthData["Duration"] > 10000).sum())
    # gets the total number of plays that lasted over 10 seconds
    monthPlaysOver60 = int((monthData["Duration"] > 60000).sum())
    # gets the total number of plays that lasted over 60 seconds

    monthUniqueTracks = len(monthData["Track"].unique())
    # grabs the number of unique tracks
    monthUniqueArtists = len(monthData["Artist"].unique())
    # grabs the number of unique artists
    monthUniqueAlbums = len(monthData["Album"].unique())
    # grabs the number of unique albums

    monthlyData = {
        "Month Start": monthStart.isoformat(),
        "Month End": pd.Timestamp(monthData["Date"].max()).isoformat(),
        "Playcount": monthPlaycount,
        "Playtime": int(monthPlaytime),
        "Over10": monthPlaysOver10,
        "Over60": monthPlaysOver60,
        "Average": f"{int(monthAvgDurMin)}:{int(monthAvgDurSec):02d}",
        "Percent": monthPlayPercent,
        "Tracks": monthUniqueTracks,
        "Artists": monthUniqueArtists,
        "Albums": monthUniqueAlbums
    }
    # forms a dictionary of some monthly stats

    currentMonthVerbose = currentMonth.strftime("%B")
    # gets the verbose name of the month (10 -> October)
    
    print(f"{timestamper()} | Statistics for {currentMonthVerbose} calculated!\n")
    # user inform

### Month/Year Ranks ###

    periodRankDF = stageFourDateFrame.copy()
    # copies the date dataframe
    periodRankDF["Year"] = periodRankDF["Date"].dt.year
    # adds a year column
    periodRankDF["Month"] = periodRankDF["Date"].dt.month_name()
    # adds a month column (uses the name of the month)
    periodRankDF["MonthNum"] = periodRankDF["Date"].dt.month
    # adds a month column (uses the number of the month)
    periodRankDF["Period"] = (periodRankDF["Date"].dt.month_name() + " " + periodRankDF["Date"].dt.year.astype(str))
    # adds a period column, which is just the month + year (eg. January 2024), used by individual months
    
    if individualMonths:
    # if the months should be treated as separate per year
        monthRanks = periodRankDF.groupby(["Period"]).agg(**{"Total Time": ("Duration", "sum"), "Playcount": ("Date", "count")}).reset_index()
        # groups by the time period, adds up the durations (renames to Total Time), counts the plays (renames to Playcount)

        if len(monthRanks) > topMonthCount:
        # if the length of the dataframe exceeds the requested amount
            monthRanks = monthRanks.nlargest(topMonthCount, sortColumn)
            # gets the requested number of top months by the sortColumn (Playcount or Total Time)

        monthRanks["Year"] = monthRanks["Period"].str[-4:].astype(int)
        # gets the last 4 characters of the period column (year), turns into int, saves as "Year" column
        monthRanks["MonthNum"] = (pd.to_datetime(monthRanks["Period"], format="%B %Y").dt.month)
        # turns the period column to datetime values, reformats to match, grabs the month number and saves as "MonthNum" column

        monthRanks = monthRanks.sort_values(by=sortColumn, ascending=False)[["Period", "Total Time", "Playcount"]]
        # sorts the dataframe by the values (total time or playcount), only stores Period | Total Time | Playcount columns (in that order)

        # monthRanks = monthRanks.sort_values(by=["Year", "MonthNum"],ascending=[False, True])[["Period", "Total Time", "Playcount"]]
        # sorts the dataframe by the period (eg. January, February... / January 2025, December 2025, February 2023), only stores Period | Total Time | Playcount columns (in that order)
        # spent an annoying amount of time getting this to work, won't delete - may use as an alt sorting method later
    else:
    # each month is shared across years
        monthRanks = periodRankDF.groupby("Month").agg(**{"Total Time": ("Duration", "sum"), "Playcount": ("Date", "count"), "MonthNum": ("MonthNum", "first")}).reset_index()
        # groups by the month, adds up the durations (renames to Total Time), counts the plays (renames to Playcount), grabs the month numbers

        if len(monthRanks) > topMonthCount:
        # if the length of the dataframe exceeds the requested amount
            monthRanks = monthRanks.nlargest(topMonthCount, sortColumn)
            # gets the requested number of top months by the sortColumn (Playcount or Total Time)
        
        monthRanks = monthRanks.sort_values(by="MonthNum", ascending=True)[["Month", "Total Time", "Playcount"]]
        # sorts the dataframe by the period (eg. January, February, March...), only stores Month | Total Time | Playcount columns (in that order)

    yearRanks = periodRankDF.groupby("Year").agg(**{"Total Time": ("Duration", "sum"), "Playcount": ("Date", "count")}).reset_index()
    # groups by the year, adds up the durations (renames to Total Time), counts the plays (renames to Playcount)

    if len(yearRanks) > topYearCount:
    # if the length of the dataframe exceeds the requested amount
        yearRanks = yearRanks.nlargest(topYearCount, sortColumn)
        # gets the requested number of top years by the sortColumn (Playcount or Total Time)

    yearRanks = yearRanks.sort_values(by="Year", ascending=False)
    # sorts the values by the year column

### Yearly Data ###

    yearStart = pd.Timestamp(currentYear.year, 1, 1)
    yearEnd = pd.Timestamp(currentYear.year + 1, 1, 1)
    # gets the start and endpoints of the pd timestamp periods (eg. 2025.1.1 - 2026.1.1)

    yearData = stageFourDateFrame[(stageFourDateFrame["Date"] >= yearStart) & (stageFourDateFrame["Date"] < yearEnd)]
    # grabs all the data between the start/end points for the year
    yearPlaycount = int(len(yearData))
    yearPlaytime = int(yearData["Duration"].sum())
    # gets the play count and time for the year

    yearSummary = pd.DataFrame()
    # a new dataframe for the year's data

    if topHistoricalCount >= 1:
    # if the summary top list option is at least 1

        yearTrackData = (yearData.groupby("Track").agg({"Duration": "sum", "Date": "count", "Artist": lambda x: ", ".join(x.unique())}).rename(columns={"Duration": "Total Time", "Date": "Playcount"})).reset_index()
        # gets the track data for the year
        topYearTracks = yearTrackData.nlargest(topHistoricalCount, sortColumn)
        # gets the x highest tracks of the year
        topYearTrackList = StageFourListHelper(topYearTracks, "Track", timeDivisor)
        # calls the helper to get the list of tracks + details

        yearArtistData = (yearData.groupby("Artist").agg({"Duration": "sum", "Date": "count"}).rename(columns={"Duration": "Total Time", "Date": "Playcount"})).reset_index()
        # gets the artist data for the month
        topYearArtists = yearArtistData.nlargest(topHistoricalCount, sortColumn)
        # gets the x highest artists of the year
        topYearArtistList = StageFourListHelper(topYearArtists, "Artist", timeDivisor)
        # calls the helper to get the list of artists + details

        yearAlbumData = (yearData.groupby("Album").agg({"Duration": "sum", "Date": "count", "Artist": "first"}).rename(columns={"Duration": "Total Time", "Date": "Playcount"})).reset_index()
        # gets the album data for the year
        topYearAlbums = yearAlbumData.nlargest(topHistoricalCount, sortColumn)
        # gets the x highest albums of the year
        topYearAlbumList = StageFourListHelper(topYearAlbums, "Album", timeDivisor)
        # calls the helper to get the list of albums + details

        yearLists = {
            "Track": topYearTrackList,
            "Artist": topYearArtistList,
            "Album": topYearAlbumList
        }
        # a dictionary with references between column names and lists

        highestMonthRank = max((len(topList) for topList in yearLists.values()), default=0)
        # goes through all the lists of top x, gets the longest length
        yearSummary["Rank"] = range(1, (highestMonthRank + 1))
        # makes a Rank column that ranges from 1 to X+1 (since len(list) is one-off)

        for x in yearLists.keys():
        # goes through the dictionary's keys (item names/strings)
            if len(yearLists[x]) > 0:
            # if the value of the matching list has at least 1 item (len > 0)
                yearSummary[x] = pd.Series(yearLists[x])
                # adds a column of x (track, album, artist, year, month...) and enters the values of that matching list (wraps in a Series to allow empty values to be added)
                # this is because you can have up to however many of eg. tracks (let's just say 100), but not necessarily as many artists (maybe 15)
                # without the pd.Series, the dataframe expects 100 values per column, since that's how big Rank is, but artists now only has 15 -> valueError, the pd.Series just fills with NaN

    yearSpentEnd = min(lastDataDate, yearEnd)
    # gets the earlier of the two - the last data stamp or the end of the year (if using incomplete data, lastDataDate < yearEnd, if using complete data, lastDataDate > yearEnd)
    yearSpent = (yearSpentEnd - yearStart).total_seconds()
    # calculates how many seconds the year has already burned through

    yearPlayPercent = (((yearPlaytime / 1000) / yearSpent) * 100)
    # calculates how much of the selected year has been spent listening to Spotify (in seconds)
    yearPlayPercent = f"{yearPlayPercent:,.2f}%" if yearPlayPercent < 100 else "~100%"
    # if the percentage is <100, uses 2 decimals, if it's 100 (or capped at 100), uses 100%

    yearAvgDurMin, yearAvgDurSec = divmod(int((yearPlaytime / yearPlaycount) / 1000), 60)
    # divides the milliseconds with the playcount, then divides with 1000 -> seconds
    yearPlaysOver10 = int((yearData["Duration"] > 10000).sum())
    # gets the total number of plays that lasted over 10 seconds
    yearPlaysOver60 = int((yearData["Duration"] > 60000).sum())
    # gets the total number of plays that lasted over 60 seconds

    yearUniqueTracks = len(yearData["Track"].unique())
    # grabs the number of unique tracks
    yearUniqueArtists = len(yearData["Artist"].unique())
    # grabs the number of unique artists
    yearUniqueAlbums = len(yearData["Album"].unique())
    # grabs the number of unique albums

    yearlyData = {
        "Year Start": yearStart.isoformat(),
        "Year End": pd.Timestamp(yearData["Date"].max()).isoformat(),
        "Playcount": yearPlaycount,
        "Playtime": int(yearPlaytime),
        "Over10": yearPlaysOver10,
        "Over60": yearPlaysOver60,
        "Average": f"{int(yearAvgDurMin)}:{int(yearAvgDurSec):02d}",
        "Percent": yearPlayPercent,
        "Tracks": yearUniqueTracks,
        "Artists": yearUniqueArtists,
        "Albums": yearUniqueAlbums
    }
    # forms a dictionary of some yearly stats

    print(f"{timestamper()} | Statistics for {currentYear} calculated!\n")
    # user inform

### User-Configured Info ###

    platformData = StageFourDictHelper(stageFourInitial.get("Platform", pd.Series()), True)
    # calls the dictionary helper with a True boolean (to normalise platform names)
    platformData = dict(sorted(platformData.items(), key=lambda item: item[1], reverse=True))
    # sorts the dictionary by the values (numbers) in descending order

    startRData = StageFourDictHelper(stageFourInitial.get("Start Reason", pd.Series()))
    # calls the dictionary helper with no boolean to get the total counts of each possible option (eg. Offline would be {False: 39590, True: 9392})
    startRData = dict(sorted(startRData.items(), key=lambda item: item[1], reverse=True))
    # sorts the dictionary by the values (numbers) in descending order

    endRData = StageFourDictHelper(stageFourInitial.get("End Reason", pd.Series()))
    endRData = dict(sorted(endRData.items(), key=lambda item: item[1], reverse=True))
    # sorts the dictionary by the values (numbers) in descending order

    shuffleData = StageFourDictHelper(stageFourInitial.get("Shuffle", pd.Series()))
    shuffleData = dict(sorted(shuffleData.items(), key=lambda item: item[1], reverse=True))
    # sorts the dictionary by the values (numbers) in descending order

    skippedData = StageFourDictHelper(stageFourInitial.get("Skipped", pd.Series()))
    skippedData = dict(sorted(skippedData.items(), key=lambda item: item[1], reverse=True))
    # sorts the dictionary by the values (numbers) in descending order

    offlineData = StageFourDictHelper(stageFourInitial.get("Offline", pd.Series()))
    offlineData = dict(sorted(offlineData.items(), key=lambda item: item[1], reverse=True))
    # sorts the dictionary by the values (numbers) in descending order

    print(f"{timestamper()} | Done grabbing configured optional data!\n")
    # user inform

    extraInfoDict = {
        "Total": totalData,
        "Yearly": yearlyData,
        "Monthly": monthlyData,
        "Platform": platformData,
        "Start Reason": startRData,
        "End Reason": endRData,
        "Shuffle": shuffleData,
        "Skipped": skippedData,
        "Offline": offlineData
    }
    # forms a dictionary of the formed extra info dictionaries

    with open(extraDataPath, "w", encoding="utf-8") as eid:
    # opens the extra data path (in write mode + ensures utf-8 encoding to not brick data)
        json.dump(extraInfoDict, eid, indent=3)
        # dumps the dictionary to file

### Summary Writer ###

    summaryDF = pd.DataFrame()
    # makes a dataframe for the summary

    topLists = {
        "Track": topTrackList,
        "Artist": topArtistList,
        "Album": topAlbumList,
        "Month": topMonthList,
        "Year": topYearList
    }
    # a dictionary with references of strings -> lists

    highestRank = max((len(topList) for topList in topLists.values()), default=0)
    # goes through all the lists of top x, gets the longest length
    summaryDF["Rank"] = range(1, (highestRank + 1))
    # makes a Rank column that ranges from 1 to X+1 (since len(list) is one-off)

    for x in topLists.keys():
    # goes through the dictionary's keys (item names/strings)
        if len(topLists[x]) > 0:
        # if the value of the matching list has at least 1 item (len > 0)
            summaryDF[x] = pd.Series(topLists[x])
            # adds a column of x (track, album, artist, year, month...) and enters the values of that matching list (wraps in a Series to allow empty values to be added)
            # this is because you can have up to however many of eg. tracks (let's just say 100), but not necessarily as many artists (maybe 15)
            # without the pd.Series, the dataframe expects 100 values per column, since that's how big Rank is, but artists now only has 15 -> valueError, the pd.Series just fills with NaN
    
    excelSheets = {
        "Total Summary": summaryDF,
        "Monthly Summary": monthSummary,
        "Yearly Summary": yearSummary,
        "Year Ranks": yearRanks,
        "Month Ranks": monthRanks,
        "Top Tracks": topTracks,
        "Top Artists": topArtists,
        "Top Albums": topAlbums,
        "Monthly Top Tracks": topMonthTracks,
        "Monthly Top Artists": topMonthArtists,
        "Monthly Top Albums": topMonthAlbums,
        "Yearly Top Tracks": topYearTracks,
        "Yearly Top Artists": topYearArtists,
        "Yearly Top Albums": topYearAlbums
    }
    # forms a dictionary of sheet name references to dataframes (easy to for loop)

    with pd.ExcelWriter(summaryXlsxPath, engine="openpyxl") as smry:
    # opens the xlsx file path
        for sheetName, dataframe in excelSheets.items():
        # goes through each sheet in the dictionary
            if not dataframe.empty:
            # if that dataframe has data
                dataframe.to_excel(smry, sheet_name=sheetName, index=False)
                # saves to the excel file with the given sheet name

    print(f"{timestamper()} | Stage 4 complete!\n")
    # user inform

    if runCharter:
    # if the boolean is enabled
        StageFive(True)
        # runs the next stage
    else:
    # boolean disabled
        print(f"{timestamper()} | Charting is disabled via config, all tasks complete!")
        # user inform





### Stage 5: Charting ###

def StageFive(liveData: bool):
    """Stage 5 / Charting function"""

    if liveData:
    # live data means "program ran through summary (stage 4) prior and has data in variables" vs reading from file
        xlsxSheets = excelSheets
        # grabs the stage 4 variable of dictionary of dataframes
        extraInfo = extraInfoDict
        # dictionary that holds extra info from summary (good for single charts / overview info)
        print(f"\n{timestamper()} | Starting Stage 5: Charting (via variable)\n")
        # user inform
    else:
    # starting from this stage
        xlsxSheets = pd.read_excel(summaryXlsxPath, sheet_name=None)
        # opens the excel file, grabs all the sheets (a dictionary of {sheetName:dataframe})

        with open(extraDataPath) as eid:
        # opens the extra info json file
            extraInfo = json.load(eid)
            # grabs the extra info from the json file
        
        print(f"\n{timestamper()} | Starting Stage 5: Charting (via file)\n")
        # user inform

    startWin.chartSignal.emit(xlsxSheets, extraInfo)
    # sends the signal with the dictionary of dataframes + dictionary to start the charter class





### Spotify Data File Selection ###

def selectDataZip() -> str:
    """Function to select the zip file"""

    gui = easygui
    # creates the file selection gui in case it's needed
    dataArray = os.listdir(configFolderPath)
    # stores the list of filenames in the config folder 
    zips = [zipP for zipP in dataArray if zipP.endswith("zip")]
    # checks the directory for files with .zip, used to select the zip file
    defaultPath = f"{configFolderPath}/*.zip"
    # forms a default path to guide the user 

    if len(zips) == 1:
    # if there's exactly 1 zip file
        zipPath = os.path.join(configFolderPath, zips[0])
        # forms the path
        print(f"{timestamper()} | Using .zip file: {zips[0]}")
        # user inform
        return zipPath
        # returns the path to the calling function

    elif len(zips) > 1:
    # if there's more than one 
        zipPath = gui.fileopenbox(title=("Please select your streaming history file"), filetypes=["*.zip"], default=defaultPath)
        # there is more than one zip file in the directory, user has to choose one
        return zipPath
        # returns the path to the calling function

    elif len(zips) == 0:
    # no zips in folder
        print(f"{timestamper()} | No .zip files in the folder\n{timestamper()} | Please add your Spotify streaming file to {configFolderPath}")
        # user inform
        os.startfile(configFolderPath)
        # opens the directory where the files need to go to
        return None
        # no return (can't)

    else:
    # Schrödinger's zip files???
        return None
        # does nothing because what situation landed you here???



### Processing Start Logic ###

def stageStarter(stage: int):
    """Function to start at a given stage (1-5)"""
    stages = {
        1: StageOne,
        2: StageTwo,
        3: StageThree,
        4: StageFour,
        5: StageFive
    }
    # dictionary of stage numbers with their functions

    if stage and stage in stages:
    # if a stage was passed, and it's found in the stage dict
        startWin.hide()
        # hides the window (console-only from now on)
        if stage == 1:
        # if the stage is 1
            spotifyZip = selectDataZip()
            # runs the zip selector, which returns the zip file path (ideally)
            if spotifyZip:
            # if a zip was found successfully
                stages[1](spotifyZip)
                # runs the first stage with the selected zip file
        elif stage < 4:
        # no required info
            stages[stage]()
            # runs the passed stage
        elif stage == 4:
        # stage 4 requires confirmation on live data or not
            StageFour(False)
            # calls the fourth stage (summary) with no live data (pulls from file)
        elif stage == 5:
        # stage 5 requires confirmation on live data or not
            StageFive(False)
            # calls the fifth stage (charter) with no live data (pulls from file)
            


### Startup ###

startApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
startWin = starterWindow()
# creates a window instance for the starter window
sys.exit(startApp.exec())
# exceutes the app task (runs the QApplication)