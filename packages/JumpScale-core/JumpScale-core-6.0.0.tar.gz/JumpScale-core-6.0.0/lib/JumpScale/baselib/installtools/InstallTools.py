# from JumpScale import j

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen
import gzip
import os
import tarfile
import sys
import shutil
import tempfile
import platform
import subprocess
import time

#how to import without extensions (jumpscale is not required)
#from core.installtools import InstallTools

class InstallTools():
    def __init__(self):
        if platform.system().lower()=="windows":
            self.TYPE="WIN"
            self.BASE="%s/"%os.environ["QBASE"].replace("\\","/")
            while self.BASE[-1]=="/":
                self.BASE=self.BASE[:-1]
            self.BASE+="/"
            self.TMP=tempfile.gettempdir().replace("\\","/")
        else:
            self.TYPE="LINUX"
            self.BASE="/opt/qself.BASE6"
            self.TMP="/tmp"
        self.debug=False

    def enableQshell(self):
        pass
        #@todo

    def download(self,url,to):
        os.chdir(self.TMP)
        print('Downloading %s ' % (url))
        handle = urlopen(url)
        with open(to, 'wb') as out:
            while True:
                data = handle.read(1024)
                if len(data) == 0: break
                out.write(data)
        handle.close()
        out.close()

    def chdir(seld,ddir):
        os.chdir(ddir)

    # def execute(self,command, timeout=60,tostdout=True):

    #     try:
    #         proc = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    #     except Exception,e:
    #         raise RuntimeError("Cannot execute cmd:%s, could not launch process, error was %s"%(command,e))
            
    #     poll_seconds = .250
    #     deadline = time.time()+timeout
    #     while time.time() < deadline and proc.poll() == None:
    #         time.sleep(poll_seconds)

    #     if proc.poll() == None:
    #         if float(sys.version[:3]) >= 2.6:
    #             proc.terminate()
    #         raise RuntimeError("Cannot execute cmd:%s, timeout"%(command))

    #     stdout, stderr = proc.communicate()

    #     if stdout.strip()=="":
    #         stdout=stderr

    #     if proc.returncode<>0:
    #         raise RuntimeError("Cannot execute cmd:%s, error was %s"%(command,stderr))

    #     return stdout

    def log(self,msg,level=0):
        print(msg)

    def isUnix(self):
        if sys.platform.lower().find("linux")!=-1:
            return True
        return False


    def isWindows(self):
        if sys.platform.lower().find("linux")==1:
            return True
        return False

    def execute(self, command , dieOnNonZeroExitCode=True, outputToStdout=False, useShell = False, ignoreErrorOutput=False):
        """Executes a command, returns the exitcode and the output
        @param command: command to execute
        @param dieOnNonZeroExitCode: boolean to die if got non zero exitcode
        @param outputToStdout: boolean to show/hide output to stdout
        @param ignoreErrorOutput standard stderror is added to stdout in out result, if you want to make sure this does not happen put on True
        @rtype: integer represents the exitcode plus the output of the executed command
        if exitcode is not zero then the executed command returned with errors
        """
        # Since python has no non-blocking readline() call, we implement it ourselves
        # using the following private methods.
        #
        # We choose for line buffering, i.e. whenever we receive a full line of output (terminated by \n)
        # on stdout or stdin of the child process, we log it
        #
        # When the process terminates, we log the final lines (and add a \n to them)
        self.log("exec:%s" % command)
        def _logentry(entry):
            if outputToStdout:
                self.log(entry)

        def _splitdata(data):
            """ Split data in pieces separated by \n """
            lines = data.split("\n")
            return lines[:-1], lines[-1]

        def _logoutput(data, OUT_LINE, ERR_LINE):
            [lines, partialline] = _splitdata(data)
            if lines:
                lines[0] = OUT_LINE + lines[0]
            else:
                partialline = OUT_LINE + partialline
            OUT_LINE = ""
            if partialline:
                OUT_LINE = partialline
            for x in lines:
                _logentry(x,3)
            return OUT_LINE, ERR_LINE

        def _logerror(data, OUT_LINE, ERR_LINE):
            [lines, partialline] = _splitdata(data)
            if lines:
                lines[0] = ERR_LINE + lines[0]
            else:
                partialline = ERR_LINE + partialline
            ERR_LINE = ""
            if partialline:
                ERR_LINE = partialline
            for x in lines:
                _logentry(x,4)
            return OUT_LINE, ERR_LINE

        def _flushlogs(OUT_LINE, ERR_LINE):
            """ Called when the child process closes. We need to get the last
                non-\n terminated pieces of the stdout and stderr streams
            """
            if OUT_LINE:
                _logentry(OUT_LINE,3)
            if ERR_LINE:
                _logentry(ERR_LINE,4)

        if command is None:
            raise ValueError('Error, cannot execute command not specified')

        try:
            import errno
            if self.isUnix():
                import subprocess
                import signal
                try:
                    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
                except Exception as ex:
                    selflog('failed to set child signal, error %s'%ex, 2)
                childprocess = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, shell=True, env=os.environ)
                (output,error) = childprocess.communicate()
                exitcode = childprocess.returncode
                
            elif self.isWindows():
                import subprocess, win32pipe, msvcrt, pywintypes

                # For some awkward reason you need to include the stdin pipe, or you get an error deep inside
                # the subprocess module if you use QRedirectStdOut in the calling script
                # We do not use the stdin.
                childprocess = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=False, shell=useShell, env=os.environ)
                output = ""; OUT_LINE = ""; ERR_LINE = ""
                childRunning = True

                while childRunning:
                    stdoutData = childprocess.stdout.readline() # The readline method will block until data is received on stdout, or the stdout pipe has been destroyed. (Will return empty string)
                                                                # Only call processes that release their stdout pipe when exiting, otherwise the method will not return when the process completed.
                                                                # When the called process starts another process and marks its handle of the stdout pipe as inheritable, the pipe will not be destroyed before both processes end.
                    if stdoutData != '':
                        output = output + stdoutData
                        (OUT_LINE, ERR_LINE) = _logoutput(stdoutData, OUT_LINE, ERR_LINE)
                    else: # Did not read any data on channel
                        if childprocess.poll() != None: # Will return a number if the process has ended, or None if it's running.
                            childRunning = False

                exitcode = childprocess.returncode
                error = "Error output redirected to stdout."

            else:
                raise RuntimeError("Non supported OS for self.execute()")

        except Exception as e:
            raise

        if exitcode!=0 or error!="":
            self.log(" Exitcode:%s\nOutput:%s\nError:%s\n" % (exitcode, output, error), 5)
            if ignoreErrorOutput!=True:
                output="%s\n***ERROR***\n%s\n" % (output,error)

        if exitcode !=0 and dieOnNonZeroExitCode:
            self.log("command: [%s]\nexitcode:%s\noutput:%s\nerror:%s" % (command, exitcode, output, error), 3)
            raise RuntimeError("Error during execution! (system.process.execute())\n\nCommand: [%s]\n\nExitcode: %s\n\nProgram output:\n%s\n\nErrormessage:\n%s\n" % (command, exitcode, output, error))

        return output        


    def expand_tar_gz(self,path,destdir,deleteDestFirst=True,deleteSourceAfter=False):

        self.lastdir=os.getcwd()
        os.chdir(self.TMP)
        basename=os.path.basename(path)
        if basename.find(".tar.gz")==-1:
            j.errorconditionhandler.raiseBug(message="Can only expand a tar gz file now %s"%path,category="installer.expand")
        tarfilename=".".join(basename.split(".gz")[:-1])
        self.delete(tarfilename)
        
        if deleteDestFirst:
            self.delete(destdir)

        if self.TYPE=="WIN":
            cmd="gzip -d %s" % path
            os.system(cmd)
        else:
            handle = gzip.open(path)
            with open(tarfilename, 'w') as out:
                for line in handle:
                    out.write(line)
            out.close()
            handle.close()

        t = tarfile.open(tarfilename, 'r')
        t.extractall(destdir)    
        t.close()

        self.delete(tarfilename)

        if deleteSourceAfter:
            self.delete(path)

        os.chdir(self.lastdir)
        self.lastdir=""

    expand=expand_tar_gz

    def getLastChangeSetBitbucket(self,account="jumpscale",reponame="jumpscale-core"):
        
        url="https://api.bitbucket.org/1.0/repositories/%s/%s/src/tip/" % (account,reponame)
        handle = urlopen(url)
        lines=handle.readlines()
        for line in lines:
            if line.find("\"node\"")!=-1:
                return line.split("\"")[3]   

    def getTmpPath(self,filename):
        return "%s/%s"%(self.TMP,filename)

    def downloadJumpScaleCore(self,dest):
        #csid=getLastChangeSetBitbucket()        
        self.download ("https://bitbucket.org/jumpscale/jumpscale-core/get/default.tar.gz","%s/pl6core.tgz"%self.TMP)
        self.expand("%s/pl6core.tgz"%self.TMP,dest)
            
    def getPythonSiteConfigPath(self):
        minl=1000000
        result=""
        for item in sys.path:
            if len(item)<minl and item.find("python")!=-1:
                result=item
                minl=len(item)
        return result

    def writefile(self,path,content):
        fo = open(path, "w")
        fo.write( content )
        fo.close()

    def delete(self,path):
        if self.debug:
            print("delete: %s" % path)
        if os.path.exists(path) or os.path.islink(path):
            if os.path.isdir(path):
                #print "delete dir %s" % path           
                if os.path.islink(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
            else:
                #print "delete file %s" % path           
                os.remove(path)

    def copytreedeletefirst(self,source,dest):
        self.delete(dest)
        if self.debug:
            print("copy %s %s" % (source,dest))
        shutil.copytree(source,dest)

    def copydeletefirst(self,source,dest):
        #try:
        #    os.remove(dest)
        #except:
        #    pass
        self.delete(dest)
        if self.debug:
            print("copy %s %s" % (source,dest))
        shutil.copy(source,dest)

    def createdir(self,path):
        if self.debug:
            print("createdir: %s" % path)
        if not os.path.exists(path) and not os.path.islink(path):
            os.makedirs(path)

    def installBaseMinimal(self):
        pldir="%s/plcore"   % self.TMP
        shutil.rmtree(pldir,True)
        self.downloadJumpScaleCore(pldir)
        pldir=os.path.join(pldir,os.listdir(pldir)[0])
        
        self.copytreedeletefirst(os.path.join(pldir,"qself.BASE6","cfg"),"%s/cfg/" % self.BASE)
        if not self.TYPE=="WIN":
            self.copydeletefirst(os.path.join(pldir,"qself.BASE6","jshell"),"%s/jshell" % self.BASE)
        self.copytreedeletefirst(os.path.join(pldir,"core"),"%s/lib/jumpscale" % self.BASE)
        #writefile("%s/lib/jumpscale/core/__init__.py"%self.BASE,"")
        self.copytreedeletefirst(os.path.join(pldir,"extensions","core"),"%s/lib/jumpscaleextensions/core" % self.BASE)
        self.copytreedeletefirst(os.path.join(pldir,"utils"),"%s/utils" % self.BASE)
        if not self.TYPE=="WIN":
            shutil.copyfile(os.path.join(pldir,"lib","python.zip"),"%s/lib/python.zip" % self.BASE)
        self.writefile("%s/lib/__init__.py"%self.BASE,"")
        try:
            os.makedirs("%s/var/log/jumpscalelogs"%self.BASE)
        except:
            pass
        try:
            os.makedirs("%s/utils"%self.BASE)
        except:
            pass
        print("minimal qself.BASE installed")
        
    def removesymlink(self,path):
        if self.TYPE=="WIN":
            try:            
                cmd="junction -d %s 2>&1 > null" % (path)
                print(cmd)
                os.system(cmd)
            except Exception as e:
                pass

    def symlink(self,src,dest):
        """
        dest is where the link will be created pointing to src
        """
        if self.debug:
            print("symlink: src:%s dest:%s" % (src,dest))
        
        #if os.path.exists(dest):
        #try:
        #    os.remove(dest)    
        #except:        
        #    pass
        self.createdir(dest)
        if self.TYPE=="WIN":
            self.removesymlink(dest)
            self.delete(dest)
        else:
            self.delete(dest)
        print("symlink %s to %s" %(dest, src))
        if self.TYPE=="WIN":
            if self.debug:
                print("symlink %s %s" % (src,dest))
            cmd="junction %s %s 2>&1 > null" % (dest,src)
            os.system(cmd)
            #raise RuntimeError("not supported on windows yet")
        else:
            os.symlink(src,dest)
        
    def replacesitecustomize(self):
        if not self.TYPE=="WIN":
            ppath="/usr/lib/python2.7/sitecustomize.py"
            if ppath.find(ppath):
                os.remove(ppath)
            self.symlink("%s/utils/sitecustomize.py"%self.BASE,ppath)
                
            def do(path,dirname,names):
                if path.find("sitecustomize")!=-1:
                    self.symlink("%s/utils/sitecustomize.py"%self.BASE,path)
            print("walk over /usr to find sitecustomize and link to new one")
            os.path.walk("/usr", do,"")
            os.path.walk("/etc", do,"")
        
