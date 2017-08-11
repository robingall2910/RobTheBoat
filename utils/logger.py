import logging
import sys
import colorlog
import logging.handlers
import os
import time
import zipfile
import codecs

debugging = False

class TimedCompressedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    # NOT ALL THE CODE IN THIS CLASS IS MINE
    """
    Extended version of TimedRotatingFileHandler that compress logs on rollover.
    """
    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """

        self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        timeTuple = time.localtime(t)
        timeName = time.strftime(self.suffix, timeTuple)
        dfn = "logs/" + timeName + ".log"
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        #print "%s -> %s" % (self.baseFilename, dfn)
        if self.encoding:
            self.stream = codecs.open(self.baseFilename, 'w', self.encoding)
        else:
            self.stream = open(self.baseFilename, 'w')
        self.rolloverAt = self.rolloverAt + self.interval
        if os.path.exists(dfn + ".zip"):
            os.remove(dfn + ".zip")
        file = zipfile.ZipFile(dfn + ".zip", "w")
        file.write(dfn, timeName + ".log", zipfile.ZIP_DEFLATED)
        file.close()
        os.remove(dfn)

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
                "DEBUG": "cyan",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red"
        },
            style = "{",
            datefmt = ""
        ))
        shandler.setLevel(logging.DEBUG)
        logging.getLogger(__package__).addHandler(shandler)
        logging.getLogger(__package__).setLevel(logging.DEBUG)

    def setupRotator(date_format, time_format):
        if not os.path.exists("logs"):
            os.mkdir("logs")
        rotator = TimedCompressedRotatingFileHandler("logs/latest.log", "d", 1)
        rotator.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "{} {}".format(date_format, time_format)))
        logging.getLogger(__package__).addHandler(rotator)


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