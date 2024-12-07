import json
from os import environ


CONFIG_FILENAME = "config.json"
MY_ID = int(environ.get("MY_ID", 1))

CONFIG = None
with open(CONFIG_FILENAME, "r") as file:
    CONFIG = json.load(file)
