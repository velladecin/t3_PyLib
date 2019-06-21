#!/usr/bin/env python2.6
from t3_PyLib.NetworkDevice import NetworkDevice

#
# Ex

class JunosLoginFail(Exception):
    def __init__(self, msg):
        super(JunosLoginFail, self).__init__(msg)

#
# Class

class Junos(NetworkDevice):
    # we translate "known" names only,
    # others must be supplied as correct
    KNOWNHOSTS = {
        "fw1.mel":  "fwdjf0101001pr",
        "fw1.syd":  "fwdjf0201001pr",
        "dms1.mel": "swdms0101001pr",
        "dms2.syd": "swdms0201001pr"
    }

    def __init__(self, name, creds=None):
        if name in self.KNOWNHOSTS:
            name = self.KNOWNHOSTS[name]

        self.name = name
        self.nameu = name.upper()
        print ">>> %s <> %s" % (self.name, self.nameu)
        self.openSsh(creds)

        if not self.loginJunos_NoHostCheck():
            raise JunosLoginFail("Could not login to Junos device: %s" % self.nameu)

        # stop Junos terminal paging output
        self.executeCmd("set cli screen-length 0")

        self.output = 1
        self.outdir = None


    #
    # Logins

    def loginJunos_NoHostCheck(self, tmout=5):
        return self.loginJunos(['StrictHostKeyChecking=no', 'UserKnownHostsFile=/dev/null'], tmout)

    def loginJunos(self, opts=[], tmout=5):
        prompt = '@%s>' % self.nameu
        passprompt = 'Password:'

        opt = ''
        if len(opts):
            opt = "-o %s" % " -o ".join(opts)

        return self.ssh.loginManual(self.name, prompt, passprompt, opt, tmout)
