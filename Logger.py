#!/usr/bin/python
import os, os.path
import sys
from datetime import datetime

class Log:
    def __init__(self, logfile):
        if os.path.isdir(logfile):
            print "Logfile is directory (not a file): %s" % logfile
            sys.exit(1)

        logdir = os.path.dirname(logfile)
        if logdir == "":
            logdir = "."

        if not os.path.isdir(logdir):
            print "Logdir does not exist: %s" % logdir
            sys.exit(2)

        self.logfile = logfile

        try:
            self.logfh = open('%s' % self.logfile, 'a', 0)
        except IOError as e:
            print "Couldn't open logfile: %s" % self.logfile

            if debug:
                print "DEBUG: %s" % str(e)

            sys.exit(3)

    def info(self, msg):
        self._log('INFO', msg)

    def warn(self, msg):
        self._log('WARN', msg)

    def crit(self, msg):
        self._log('CRIT', msg)

    def close(self):
        self.logfh.close()


    #
    # protected

    def _log(self, level, msg):
        now = self.__now()
        self.logfh.write("%s [%s]  %s\n" % (now, level, msg))


    #
    # private

    def __now(self, format="%Y-%m-%d %H:%M:%S"):
        return datetime.today().strftime(format)
