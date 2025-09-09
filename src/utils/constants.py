import platform
from pathlib import Path
import pathlib 
import os 

PUBLISHER = "NeuroProxy"
PRODUCT_NAME = "LiveLoom"
VERSION = "0.0.1"

# ALL APP DATA
system = platform.system()
if system == "Windows":
    base = pathlib.Path(os.environ["PROGRAMDATA"])
    base_app = pathlib.Path(os.environ["APPDATA"])
elif system == "Darwin":
    base = pathlib.Path("/Library/Application Support")
else:  # Linux
    base = pathlib.Path("/opt")

ROOT_APP_DIR = base_app.joinpath(PUBLISHER, PRODUCT_NAME,VERSION)

LOGGER_NAME = PRODUCT_NAME.lower().replace(" ", "_").lower()
LOGGER_DIR = ROOT_APP_DIR.joinpath("logs")
SESSION_DIR = ROOT_APP_DIR.joinpath("sessions")

SETTINGS_FILE = ROOT_APP_DIR.joinpath("settings.json")
# make directories
os.makedirs(LOGGER_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)
