#!/usr/bin/python
import pexpect


class Ssh:
    def __init__(self):
        return


    #
    # Public

    def loginCmts_NoHostCheck(self, cmts, uname, passw):
        return self.loginCmts(cmts, uname, passw, ['StrictHostKeyChecking=no', 'UserKnownHostsFile=/dev/null'])

    def loginCmts(self, cmts, uname, passw, opts=[], tmout=5):
        cmtsprompt = '%s#' % cmts.upper()
        passprompt = 'password:'

        return self.login(cmts, uname, passw, cmtsprompt, passprompt, opts, tmout)

    def login(self, host, uname, passw, prompt, passprompt, opts=[], tmout=10):
        opt = ''
        if len(opts):
            opt = "-o %s" % " -o ".join(opts)

        ssh = pexpect.spawn('ssh %s %s@%s' % (opt, uname, host))

        try:

            exp = [passprompt, 'Are you sure you want to continue connecting']
            result = ssh.expect(exp, timeout=tmout)

            if result == 1: # new SSH key
                ssh.sendline('yes')
                ssh.expect(passprompt, timeout=5)

            ssh.sendline(passw)
            ssh.expect(prompt, timeout=5)

        except (pexpect.TIMEOUT, pexpect.EOF):
            return False

        self.session = ssh
        self.prompt = prompt

        return True

    def cmdCmts(self, cmd, tmout=60):
        self.session.sendline(cmd)
        self.session.expect(self.prompt, timeout=tmout)

        output = self.session.before

        return output.split('\r\n')
        
    def close(self):
        self.session.close()

        
