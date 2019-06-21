#!/usr/bin/env python2.6
import re
from t3_PyLib.NetworkDevice import NetworkDevice

#
# Ex

class CmtsBadName(Exception):
    def __init__(self, msg):
        super(CmtsBadName, self).__init__(msg)

class CmtsLoginFail(Exception):
    def __init__(self, msg):
        super(CmtsLoginFail, self).__init__(msg)

#
# Class

class Cmts(NetworkDevice):
    def __init__(self, name, sftp=0, creds=None):
        origname = name
        name = str(name) # accept int

        # 1
        if re.search("^\d$", name):
            name = "SWCMT%s" % name.zfill(7)

        # swcmt1
        if len(name) < 12:
            f = name[:5]
            s = name[5:].zfill(7)
            name = "%s%s" % (f, s)

        # swcmt0000001
        if len(name) != 12 or not re.search("^swcmt\d{7}$", name, re.IGNORECASE):
            raise CmtsBadName("Bad CMTS name format: %s" % origname)

        self.name = name
        self.nameu = name.upper()
        self.openSsh(creds)

        if not self.__login(sftp):
            raise CmtsLoginFail("Could not login to CMTS: %s" % self.nameu)

        self.output = 1
        self.outdir = None


    #
    # Logins

    def loginCmts_NoHostCheck(self, tmout=5):
        return self.loginCmts(['StrictHostKeyChecking=no', 'UserKnownHostsFile=/dev/null'], tmout)

    def loginCmts_SFTP(self, tmout=20):
        cmtsprompt = "sftp>"
        passprompt = "password:"

        return self.ssh.loginManual_SFTP(self.name, cmtsprompt, passprompt, tmout)

        return 1

    def loginCmts(self, opts=[], tmout=5):
        cmtsprompt = '%s#' % self.nameu
        passprompt = 'password:'

        opt = ''
        if len(opts):
            opt = "-o %s" % " -o ".join(opts)

        return self.ssh.loginManual(self.name, cmtsprompt, passprompt, opt, tmout)

    #
    # Private

    def __login(self, sftp=0):
        if sftp:
            return self.loginCmts_SFTP()
        else:
            return self.loginCmts_NoHostCheck()
