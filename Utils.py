#!/usr/bin/python
import socket, signal
import re
from subprocess import PIPE, STDOUT, Popen


#
# Vars

SSHK = '/root/HFCNOC_T3/SCRIPT_USER_CREDS__do_not_remove/.ssh/id_rsa'
SITE = { "1": "Mel", "2": "Syd" }


#
# Exceptions

class CmdTimeoutException(Exception):
    def __init__(self, msg):
        super(CmdTimeoutException, self).__init__(msg)
class CmdReturnNonZeroException(Exception):
    def __init__(self, msg):
        super(CmdReturnNonZeroException, self).__init__(msg)


#
# Defs

def alarm_handler(signum, frame):
    raise CmdTimeoutException('Command Timeout!');

def shellCmd(command, timeout=20):
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)

    try:
        proc = Popen(
            command,
            stderr = STDOUT,
            stdout = PIPE,
            #shell = True
        )

        outdata, outerror = proc.communicate()
        retcode = proc.returncode

        signal.alarm(0)

        if retcode != 0:
            raise CmdReturnNonZeroException("Non-zero (%d) return for command" % retcode)

    except CmdTimeoutException, e:
        return None, e
    except CmdReturnNonZeroException, e:
        return None, e

    outdata_list = []
    for line in outdata.splitlines():
        if not len(line):
            continue

        outdata_list.append(line)

    return 1, outdata_list

def getDomsSite(site="local"):
    ret = [ "Could not identify DOMS site" ]

    if site == "local" or site == "other":
        s = re.search('^[a-z]+0(\d)\d+', socket.gethostname().lower())

        try:
            snum = s.group(1)
            SITE[snum]
        except (AttributeError, KeyError) as e:
            print e.args
            return ret

        if site == "other": # have only 2 sites (at the moment..)
            if snum == "1":
                snum = "2"
            else:
                snum = "1"

        ret = [ SITE[snum] ]
    elif site == "all":
        ret = []
        for snum in sorted(SITE.keys()):
            ret.append(SITE[snum])
    else:
        print "Unknown site requested: %s" % site

    return ret

def getIp(host):
    try:
        ip = socket.gethostbyname(host)
        return ip
    except socket.error:
        return "No resolution"
