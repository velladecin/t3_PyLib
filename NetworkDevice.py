#!/usr/bin/env python2.6
import re
import random
import time
from t3_PyLib.Ssh import *

class NetworkDevice:

    #
    # SSH

    def openSsh(self, creds=None):
        if creds:
            self.ssh = Ssh(creds)
        else:
            self.ssh = Ssh()

    def closeSsh(self):
        self.ssh.close()


    #
    # CMD ingests

    def ingestCmdList(self, newcmdlist):
        if isinstance(newcmdlist, list):
            self.cmdlist = newcmdlist
            return self.cmdlist

        return False

    def ingestCmdFile(self, file):
        self.cmdlist = []

        try:
            with open(file) as f:
                for line in f.read().splitlines():
                    if re.match('#', line):
                        continue

                    if re.match('^$', line):
                        continue

                    self.cmdlist.append(line)
        except (IOError, OSError) as e:
            print "Could not read file '%s': %s" % (file, str(e))
            return False

        return self.cmdlist


    #
    # CMD exec

    def executeCmdList(self):
        if not len(self.cmdlist):
            return False

        fullout = ''
        for cmd in self.cmdlist:
            out = [self.name]
            r = self.executeCmd(cmd, 120)   # increase timeout - some cmds take long time
                                            # should we filter by eg: scm?
            out.extend(r)
            outx = "\n".join(out)

            if self.output:
                # attempt to stop threads writing over each other
                time.sleep(round(random.uniform(0.0, 1.0), 1))
                print(outx)

            fullout = "%s\n\n%s" % (fullout, outx)

        if self.outdir:
            try:
                with open("%s/%s" % (self.outdir, self.name), "a") as f:
                    f.write("%s\n\n" % fullout)
            except (IOError, OSError):
                print "WARN: CMTS %s - could not write output" % self.name

        ok = "%s - OK" % self.name
        if self.output:
            ok = "%s\n" % ok

        print ok
        return 1

    def executeCmd(self, cmd, tmout=30):
        return self.ssh.cmdExec(cmd, tmout)


    #
    # Getters

    def getName(self): return self.name
    def getCmdList(self): return self.cmdlist


    #
    # Setters

    def setOutdir(self, outdir): self.outdir = outdir
    def setOutput(self, output): self.output = output


    #
    # Other

    def disconnect(self): self.closeSsh()
