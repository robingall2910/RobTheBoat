import os

from utils.logger import log

class Bootstrap:
    def run_checks():
        if not os.path.isdir("data"):
            log.warning("No folder named \"data\" was found, creating one... (This message is harmless)")
            os.makedirs("data")

        if not os.path.isdir("assets"):
            log.critical("There is no folder named \"assets\"! Please go to the github repo and download the assets folder!")
            os._exit(1)
