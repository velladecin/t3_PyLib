#!/usr/bin/python
import pexpect, getpass
import os, os.path
import sys, re
from t3_PyLib import Utils

class Ssh:
    def __init__(self, creds=None):
        if not creds:
            creds = Creds()

        self.creds = creds


    # TODO
    # SSH key use not yet tested as at 25/Feb 2019


    #
    # Public

    def close(self):
        self.session.close()

    def cmdExec(self, cmd, tmout=60):
        self.session.sendline(cmd)
        self.session.expect(self.prompt, timeout=tmout)

        output = self.session.before
        return output.split('\r\n')

    def loginManual_SFTP(self, host, prompt, passprompt, tmout=10):
        # accepting uname/passwd only
        creds = self.creds.getCreds()

        if not "creds" in creds:
            print "CRITICAL: Keys not accepted by SFTP"
            return False

        uname, passwd = creds["creds"]
        sftp = pexpect.spawn('sftp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %s@%s' % (uname, host))

        try:
            exp = ['Are you sure you want to continue connecting', passprompt]
            result = sftp.expect(exp, timeout=tmout)

            if result == 0: # Unknown fingerprint
                sftp.sendline('yes')
                sftp.expect([passprompt])

            sftp.sendline(passwd)
            sftp.expect(prompt, timeout=tmout)

        except pexpect.TIMEOUT as e:
            print "*** !!!!!!! *** Host: %s connection timeout: is password correct?" % host
            return False
        except pexpect.EOF as e:
            print "*** !!!!!!! *** Host: %s unknown, or could not connect (EOF)" % host
            return False

        self.session = sftp
        self.prompt = prompt

        return True

    def loginManual(self, host, prompt, passprompt, opt='', tmout=10):
        # passw beats sshkey!
        creds = self.creds.getCreds()

        if "creds" in creds:
            uname, passwd = creds["creds"]
            ssh = pexpect.spawn('ssh %s -q %s@%s' % (opt, uname, host))
        else:
            uname, sshkey = creds["sshkey"]
            ssh = pexpect.spawn('ssh %s -qi %s %s@%s' % (opt, sshkey, uname, host))

        try:
            exp = ['Are you sure you want to continue connecting', passprompt]
            result = ssh.expect(exp, timeout=tmout)

            # Assumption:
            # when 'passwd' is not defined we're using SSH key

            if result == 0: # Unknown fingerprint
                ssh.sendline('yes')

                try:
                    passwd
                except NameError:
                    # SSH key
                    pass
                else:
                    # passw
                    ssh.expect([passprompt])
                    ssh.sendline(passwd)

            if result == 1:
                try:
                    ssh.sendline(passwd)
                except NameError as e:  # password is asked but we don't have it defined
                                        # therefore (supposedly) ssh key was used..
                    print str(e)
                    print "CRITICAL: SSH key not accepted by remote"
                    return False

            ssh.expect(prompt, timeout=tmout)

        except pexpect.TIMEOUT as e:
            print "*** !!!!!!! *** Host: %s connection timeout: is password correct?" % host
            return False
        except pexpect.EOF as e:
            print "*** !!!!!!! *** Host: %s unknown, or could not connect (EOF)" % host
            return False

        self.session = ssh
        self.prompt = prompt

        return True


class Creds(object):
    def __init__(self, uname='', passwd='', sshkey=''):
        # uname / passwd take precedence over SSH key.
        # Should probs be the other way around but not in NBN :O

        if uname:
            self.uname = uname

            if passwd:
                self.passwd = passwd
            elif sshkey:
                self.sshkey = sshkey
            else:
                self.__askCreds(uname)
        else:
            self.__askCreds()

    def changeCreds(self, uname='', passwd=''):
        if uname and passwd:
            self.uname = uname
            self.passwd = passwd
        elif uname:
            self.__askCreds(uname)
        else:
            self.__askCreds()

    # self.uname should always exist

    def changeSshkey(self, sshkey):
        self.sshkey = sshkey

    def getCreds(self):
        try:
            return {"creds": [self.uname, self.passwd]}
        except AttributeError:
            return {"sshkey": [self.uname, self.sshkey]}

    def getUname(self):
        return self.uname

    def getPasswd(self):
        try:
            return self.passwd
        except AttributeError:
            return None

    def getSshkey(self):
        try:
            return self.sshkey
        except AttributeError:
            return None

    def __askCreds(self, uname=''):
        if not uname:
            logname = Utils.shellCmd("logname")

            if logname[0]:
                uname = logname[1][0]
            else:
                uname = str(raw_input("Enter username: "))

        self.uname = uname

        # HACK!
        if self.uname == "viktorvillafuerte":
            hackcreds = FileCreds()
            self.passwd = hackcreds.getPasswd()
        else:
            self.__askPasswd(uname)

    def __askPasswd(self, uname):
        self.passwd = getpass.getpass("Enter password for %s: " % uname)

class FileCreds(Creds):
    def __init__(self, cfile="/bin/creds"):
        uname, passwd = self.__getCredsFromFile(cfile)
        super(FileCreds, self).__init__(uname, passwd)

    def updateCreds(self, cfile="/bin/creds"):
        # new creds file or updated
        uname, passwd = self.__getCredsFromFile(cfile)
        super(FileCreds, self).changeCreds(uname, passwd)


    #
    # Private

    def __getCredsFromFile(self, cfile):
        if not cfile or not os.path.isfile(cfile) or not os.access(cfile, os.X_OK):
            print "CRITICAL: Invalid creds file: %s" % cfile
            sys.exit(1)

        res = Utils.shellCmd(cfile)
        creds = res[1][0].split()
        splitat = re.sub('^0*', '', creds[0])

        uname = ""
        passwd = ""

        count = 0
        for o in creds[1:]:
            c = chr(int(o, 8))

            if count < int(splitat):
                uname = "%s%s" % (uname, c)
            else:
                passwd = "%s%s" % (passwd, c)

            count += 1

        if not uname or not passwd:
            print "CRITICAL: Could not process creds file %s" % cfile
            sys.exit(1)

        self.cfile = cfile

        return uname, passwd

