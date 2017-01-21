import logging
import sys
import colorlog

debugging = False

class log:
    def init():
        if len(logging.getLogger("").handlers) > 1:
            return

        shandler = logging.StreamHandler(stream=sys.stdout)
        shandler.setFormatter(colorlog.LevelFormatter(
            fmt = {
                "DEBUG": "{log_color}[{levelname}] {message}",
                "INFO": "{log_color}[{levelname}] {message}",
                "WARNING": "{log_color}[{levelname}] {message}",
                "ERROR": "{log_color}[{levelname}] {message}",
                "CRITICAL": "{log_color}[{levelname}] {message}"
            },
            log_colors = {
                "DEBUG":    "cyan",
                "INFO":     "white",
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "bold_red"
        },
            style = "{",
            datefmt = ""
        ))
        shandler.setLevel(logging.DEBUG)
        logging.getLogger(__package__).addHandler(shandler)
        logging.getLogger(__package__).setLevel(logging.DEBUG)

    def enableDebugging():
        global debugging
        debugging = True

    def debug(msg):
        if debugging:
            logging.getLogger(__package__).debug(msg)

    def info(msg):
        logging.getLogger(__package__).info(msg)

    def warning(msg):
        logging.getLogger(__package__).warning(msg)

    def error(msg):
        logging.getLogger(__package__).error(msg)

    def critical(msg):
        logging.getLogger(__package__).critical(msg)
