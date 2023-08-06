#
# XenRT: Test harness for Xen and the XenServer product family
#
# SSH interface
#
# Copyright (c) 2006 XenSource, Inc. All use and distribution of this
# copyrighted material is governed by and subject to terms and
# conditions as licensed by XenSource, Inc. All other rights reserved.
#

import socket, string, sys, os, os.path, traceback, time
import paramiko, logging

SSHPORT = 22

# Symbols we want to export from the package.
__all__ = ["SSHSession",
           "SFTPSession",
           "SSHCommand",
           "SSH"]

class SSHSession:
    def __init__(self,
                 ip,
                 username="root",
                 timeout=300,
                 password=None):
        self.logger = logging.getLogger("simplessh")
        self.toreply = 0
        self.trans = None
        reply = None
        for tries in range(3):
            self.trans = None
            try:
                self.connect(ip, username, password, timeout)
            except Exception, e:
                traceback.print_exc(file=sys.stderr)
                desc = str(e)
                self.logger.debug("SSH exception %s" % (desc))
                if string.find(desc, "Signature verification") > -1 or \
                        string.find(desc,
                                    "Error reading SSH protocol banner") > -1:
                    # Have another go
                    try:
                        self.close()
                    except:
                        pass
                    time.sleep(1)
                    reply = e
                    continue
                self.reply = e
                self.toreply = 1
                self.close()
                break
            self.logger.debug("done")
            # If we get here we have successfully opened a connection
            return
        # Even after retry(s) we didn't get a connection
        self.reply = reply
        self.toreply = 1
        self.close()

    def connect(self, ip, username, password, timeout):
        self.logger.debug("connect")
        sock = socket.create_connection((ip, SSHPORT), timeout)
            
        # Create SSH transport.
        self.logger.debug("transport")
        self.trans = paramiko.Transport(sock)
        self.trans.set_log_channel("")
            
        # Negotiate SSH session synchronously.
        goes = 1
        while goes > 0:
            try:
                self.logger.debug("start_client")
                self.trans.start_client()
                goes = 0
            except Exception, e:
                goes = goes - 1
                if goes > 0:
                    self.logger.warning("Retrying SSHSession connection")
                    time.sleep(10)
                else:
                    raise e
            
        # Authenticate session. No host key checking is performed.
        self.logger.debug("auth")
        self.logger.debug("Using SSH password %s" % (password))
        self.trans.auth_password(username, password)
        if not self.trans.is_authenticated():
            raise Exception("Problem with SSH authentication")

    def open_session(self):
        self.logger.debug("open_session")
        return self.trans.open_session()

    def close(self):
        if self.trans:
            self.trans.close()
            self.trans = None

    def __del__(self):
        self.close()

class SFTPSession(SSHSession):
    """An SFTP session guarded for target lockups."""
    def __init__(self,
                 ip,
                 username="root",
                 timeout=300,
                 password=None):
        self.logger = logging.getLogger("simplessh")
        self.logger.debug("SFTP session to %s@%s" % (username, ip))
        self.ip = ip
        self.username = username
        self.timeout = timeout
        self.password = password
        SSHSession.__init__(self,
                            ip,
                            username=username,
                            timeout=timeout,
                            password=password)
        try:
            # We do this rather than the simple trans.open_sftp_client() because
            # if we don't then we don't get a timeout set so we can hang forever
            c = self.trans.open_channel("session")
            c.settimeout(timeout)
            c.invoke_subsystem("sftp")
            self.client = paramiko.SFTPClient(c)
        except Exception, e:
            self.reply = e
            self.toreply = 1
            self.close()

    def getClient(self):
        # This is UNSAFE - the client object may change if we auto reconnect!
        return self.client

    def check(self):
        # Check if the connection is still active, if not, try and re-open the
        # connection (this handles the case where the connection has dropped
        # due to a transient network error)...

        alive = True

        # First see if the transport is alive
        if not self.trans.is_active():
            alive = False
        else:
            try:
                d = self.client.listdir()
            except:
                alive = False

        if not alive:
            self.logger.debug("SFTP session appears to have gone away, "
                                   "attempting to reconnect...")
            self.__init__(self.ip,
                          username=self.username,
                          timeout=self.timeout,
                          password=self.password)

    def close(self):
        if self.client:
            try:
                self.client.close()
            except Exception, e:
                self.logger.debug("SFTP close exception %s" % (str(e)))
        if self.trans:
            try:
                self.trans.close()
            except Exception, e:
                self.logger.debug("SFTP trans close exception %s" %
                                       (str(e)))

    def copyTo(self, source, dest, preserve=True):
        self.logger.debug("SFTP local:%s to remote:%s" % (source, dest))
        self.client.put(source, dest)
        if preserve:
            st = os.lstat(source)
            if preserve == True:
                self.client.chmod(dest, st.st_mode)
            self.client.utime(dest, (st.st_atime, st.st_mtime))

    def copyFrom(self, source, dest, preserve=True, threshold=None,
                 sizethresh=None):
        self.logger.debug("SFTP remote:%s to local:%s" % (source, dest))
        self.check()
        st = self.client.stat(source)
        if threshold and st.st_mtime < threshold:
            self.logger.debug("Skipping %s, too old" % (source))
            return
        elif sizethresh and st.st_size > long(sizethresh):
            self.logger.debug("Skipping %s, too big (%u)" %
                                   (source, st.st_size))
            return
        self.client.get(source, dest)
        if preserve:
            if preserve == True:
                os.chmod(dest, st.st_mode)
            os.utime(dest, (st.st_atime, st.st_mtime))

    def copyTreeTo(self, source, dest, preserve=True):
        """Recursive copy to the remote host

        source: local directory being root of the tree
        dest:   remote directory to be the new root of the tree
        """
        self.logger.debug("SFTP recursive local:%s to remote:%s" %
                               (source, dest))
        self.check()
        source = os.path.normpath(source)
        dirs = os.walk(source)
        for dir in dirs:
            (dirname, dirnames, filenames) = dir
            # Create the remote directory
            dirname = os.path.normpath(dirname)
            relpath = dirname[len(source):]
            if len(relpath) > 0 and relpath[0] == "/":
                relpath = relpath[1:]
            targetpath = os.path.normpath(os.path.join(dest, relpath))
            try:
                self.client.lstat(targetpath)
                # Already exists
                if preserve == True:
                    self.client.chmod(targetpath, os.lstat(dirname).st_mode)
            except IOError, e:
                self.client.mkdir(targetpath, os.lstat(dirname).st_mode)
            # Copy all the files in
            for file in filenames:
                srcfile = os.path.join(dirname, file)
                dstfile = os.path.join(targetpath, file)
                st = os.lstat(srcfile)
                self.client.put(srcfile, dstfile)
                if preserve:
                    if preserve == True:
                        self.client.chmod(dstfile, st.st_mode)
                    self.client.utime(dstfile, (st.st_atime, st.st_mtime))

    def copyTreeFromRecurse(self, source, dest, preserve=True, threshold=None,
                            sizethresh=None):
        # make sure local destination exists
        if not os.path.exists(dest):
            os.makedirs(dest)
        if preserve:
            os.chmod(dest, self.client.lstat(source).st_mode)
        d = self.client.listdir(source)
        for i in d:
            try:
                dummy = self.client.listdir("%s/%s" % (source, i))
                isdir = True
            except:
                isdir = False                
            if isdir:
                self.copyTreeFromRecurse("%s/%s" % (source, i),
                                         "%s/%s" % (dest, i),
                                         preserve=preserve,
                                         threshold=threshold,
                                         sizethresh=sizethresh)
            else:
                self.logger.debug("About to copy %s/%s" % (source, i))
                st = self.client.stat("%s/%s" % (source, i))
                if threshold and st.st_mtime < threshold:
                    self.logger.debug("Skipping %s/%s, too old" %
                                           (source, i))
                elif sizethresh and st.st_size > long(sizethresh):
                    self.logger.debug("Skipping %s/%s, too big (%u)" %
                                           (source, i, st.st_size))
                else:
                    self.client.get("%s/%s" % (source, i),
                                    "%s/%s" % (dest, i))
                    if preserve:
                        if preserve == True:
                            os.chmod("%s/%s" % (dest, i), st.st_mode)
                        os.utime("%s/%s" % (dest, i),
                                 (st.st_atime, st.st_mtime))

    def copyTreeFrom(self, source, dest, preserve=True, threshold=None,
                     sizethresh=None):
        """Recursive copy from the remote host

        source: remote directory being root of the tree
        dest:   local directory to be the new root of the tree
        """
        self.logger.debug("SFTP recursive remote:%s to local:%s" %
                               (source, dest))
        self.check()
        self.copyTreeFromRecurse(source,
                                 dest,
                                 preserve=preserve,
                                 threshold=threshold,
                                 sizethresh=sizethresh)

    def __del__(self):
        SSHSession.__del__(self)                

class SSHCommand(SSHSession):
    """An SSH session guarded for target lockups."""
    def __init__(self,
                 ip,
                 command,
                 username="root",
                 timeout=300,
                 password=None):
        SSHSession.__init__(self,
                            ip,
                            username=username,
                            timeout=timeout,
                            password=password)
        self.command = command
        if string.find(command, "\n") > -1 and not newlineok:
            self.logger.warning("Command with newline: '%s'" % (command))
        try:
            self.client = self.open_session()
            self.logger.debug("settimeout")
            self.client.settimeout(timeout)
            self.logger.debug("set_combine_stderr")
            self.client.set_combine_stderr(True)
            self.logger.debug("exec_command")
            self.client.exec_command(command)
            self.logger.debug("shutdown(1)")
            self.client.shutdown(1)            
            self.logger.debug("makefile")
            self.fh = self.client.makefile()
            self.fhstderr = self.client.makefile_stderr()
        except Exception, e:
            traceback.print_exc(file=sys.stderr)
            self.reply = e
            self.toreply = 1
            self.close()
        self.logger.debug("done (2)")

    def getResponse(self, allowError):
        """Process the output and result of the command.

        @param retval: Whether to return the result code (default) or 
            stdout as a string.
    
            string  :   Return a stdout as a string.
            code    :   Return the result code. (Default). 
                  
            If "string" is used then a failure results in an exception.
 
        """

        ret = SSHResponse()

        if self.toreply:
            if not allowError:
                raise self.reply
            ret.errorcode = self.reply
        reply = ""

        for l in self.fh.xreadlines():
            ret.stdout += l
       
    
        for l in self.fhstderr.xreadlines():
            ret.sterr += l

        self.logger.debug("recv_exit_status")
        self.exit_status = self.client.recv_exit_status()
        
        # Local clean up.
        self.logger.debug("close (2)")
        self.close()
        
        if not self.exit_status == 0:
            if not allowError:
                raise Exception("SSH command exited with error (%s) - %s" %
                             (self.command, self.exit_status))
            else:
                ret.errorcode = self.exit_status

        self.logger.debug("done (3)")
        return ret
    
    def __del__(self):
        SSHSession.__del__(self)   

class SSHResponse(object):
    def __init__(self):
        self.stdout = ""
        self.stderr = ""
        self.errorcode = 0

def SSH(ip,
        command,
        username="root",
        timeout=300,
        allowError=False,
        password=None):
    tries = 0
    logger = logging.getLogger("simplessh")
    while True:
        tries = tries + 1
        
        if tries > 1:
            logger.debug("SSH %s@%s %s (attempt %u)" % (username, ip, command, tries))
        else:
            logger.debug("SSH %s@%s %s" % (username, ip, command))
        
        try:
            s = SSHCommand(ip,
                           command,
                           username=username,
                           timeout=timeout,
                           password=password)
            reply = s.getResponse(allowError)
            return reply
        except Exception, e:
            if tries >= 3:
                raise
            if string.find(str(e), "SSH command exited with error") > -1:
                raise
            logger.warning("Retrying ssh connection %s@%s %s after %s"
                                    % (username, ip, command, str(e)))
            time.sleep(5)
