

import os
import sys
import imp
import hashlib
import traceback
import zipimport
import threading

from JumpScale import j

class BasePMExtension(object):
    """
    can be just the info of an extension or a fully loaded object (instance from class which represents extension)
    these BasePMEXtension objects are being put on q.[one or more PMExtensionsGroupObjects].[PMExtensionObject]
    """
    def __init__(self, extensionPath, moduleName, className, pmExtensionName,priority=5,qlocation=""):
        """
        Constructor for BasePMExtension instances.

        @param extensionPath: path of package of extension
        @type extensionPath: string
        @param moduleName: is filename (withoug .py) which includes class
        @type moduleName: string
        @param className: name of the root class of this extension
        @type className: string
        @param pmExtensionName: name used to expose class under q.[one or more extensionsgroup's].[pmExtensionName]
        @type pmExtensionName: string
        """
        self._activation_lock = threading.Lock()

        if not j.basetype.dirpath.check(extensionPath):
            raise ValueError('Invalid extension path %s, not a folder' %
                    extensionPath)
        if not j.basetype.string.check(moduleName):
            raise ValueError('Invalid moduleName provided, not a string')
        if not j.basetype.string.check(className):
            raise ValueError('Invalid className provided, not a string')

        self.activated = False              #is extension already loaded or not
        self.moduleInfo = None              #is python info about module, is output of find_module of http://docs.python.org/lib/module-imp.html
        self.instance = None                #is instance of BasePMExtension
        self.extensionPath = extensionPath
        self.moduleName = moduleName
        self.className = className
        self.pmExtensionName = pmExtensionName
        self.priority=5
        self.qlocation=qlocation

    def activate(self):
        """
        load extension (create instance) = lazy loading
        """
        if self.activated:
            return

        self._activation_lock.acquire()
        try:
            # Might be activated now as well, so re-check
            if not self.activated:
                self._activate()
                # Set activated to true only after activation
                self.activated = True
        finally:
            self._activation_lock.release()

    def _activate(self):
        """Internal activate method, only called if not yet activated"""
        classModule = self._loadClassModule()

        self.classDefinition = getattr(classModule, self.className)

        #make instance of definition of class
        try:
            self.instance = self.classDefinition()
            self.instance.pm_extensionpath=self.extensionPath 
            self.instance.pm_qlocation=self.qlocation
            pass
        except Exception, e:
            #Get exception type, exception instance and backtrace
            t, v, tb = sys.exc_info()
            self._handleCreateInstanceException(e,t, v, tb)

    def _handleCreateInstanceException(self, e,t, v, tb):
        #Display
        msg= 'An error occured while creating an instance of the %s extension\n' % self.moduleName
        msg+= 'Extension path: %s\n\n' % self.extensionPath
        msg+='Exception: %s (type %s)\n\n' % (str(v), v.__class__.__name__)
        stack = traceback.extract_tb(tb)
        last_frame = stack[-1]
        last_file = last_frame[0][len(self.extensionPath):]
        last_line = last_frame[1]
        last_code = last_frame[3]
        msg+= 'The exception occurred in %s on line %d: %s\n\n' % (last_file, last_line, last_code)
        print msg
        j.errorconditionhandler.raiseBug(msg,pythonTraceBack=tb,category="extensions.init")
        
        if not j.application.shellconfig.debug:
            print 'To see a full error report, check your logserver or run Q-Shell using debug mode'
            # Reset TTY
            # See above for more info
            try:
                import termios
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, __IPYTHON__.tty_settings)
            except:
                pass
            j.application.stop()
        else:
            j.application.stop()

    def _handleLoadClassModuleException(self, t, v, tb):
        #Send to logserver
        if j.application.shellconfig.ipython:
            j.application.shellconfig.interactive=True


        #Display
        msg='An error occured while loading the %s extension\n' % self.moduleName
        msg+= 'Extension path: %s\n' % self.extensionPath
        msg+= 'Exception: %s (type %s)\n' % (str(v), v.__class__.__name__)

        stack = traceback.extract_tb(tb)
        last_frame = stack[-1]
        last_file = last_frame[0][len(self.extensionPath):]
        last_line = last_frame[1]
        last_code = last_frame[3]
        msg+= 'The exception occurred in %s on line %d: %s\n\n' % (last_file, last_line, last_code)        
        print msg
        j.errorconditionhandler.raiseBug(msg,pythonTraceBack=tb,category="extensions.load")
        
        j.application.stop()

    def _loadClassModule(self):
        """Load the class module for this extension"""
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "jumpscale Extension %s (at %s)" % (self.pmExtensionName, self.extensionPath)

class PMExtension(BasePMExtension):
    """Extension class for 'normal' (non-zipped) extensions"""
    def _loadClassModule(self):
        """Load the class module for this extension from the .py file"""
        cleanedPath = os.path.abspath(self.extensionPath)
        sys.path.append(cleanedPath)
        # Make sure the sys.path is cleaned up by using a try...finally
        try:
            j.errorconditionhandler.lastAction='Try to load in %s %s ' % (self.extensionPath, self.moduleName)
            self.moduleInfo = imp.find_module(self.moduleName, [self.extensionPath, ])
            # Make sure the module file handle is closed by using a
            # try...finally
            try:
                extensionName = os.path.basename(self.extensionPath)
                j.logger.log("loadmodule: extensionName:%s, moduleName:%s" % (extensionName, self.moduleName), 8)
                moduleName = self._createModuleName()
                if moduleName in sys.modules:
                    mod = sys.modules[moduleName]
                else:
                    #This could fail if the module loading errors out. We'll catch this,
                    #display a message providing info about the failing extension, then
                    #raise the original exception
                    mod = imp.load_module(moduleName, *self.moduleInfo)
                j.errorconditionhandler.lastAction=""
                return mod
            except Exception, e:
                #Get exception type, exception instance and backtrace
                t, v, tb = sys.exc_info()
                v = "Error Loading Extention : %s, File: %s, Error: %s" % (self.moduleName, self.moduleInfo[1], v)         
                self._handleLoadClassModuleException(t, v, tb)
            finally:
                # As mentioned in # http://docs.python.org/library/imp.html#imp.load_module
                # we should close the module file handle here.
                self.moduleInfo[0].close()
        finally:
            sys.path.remove(cleanedPath)

    def _createModuleName(self):
        """
        Create a unique, repeatable module name for this extension

        Because it is repeatable, we can check if the import already happened,
        avoiding double imports.
        """
        cleanedPath = os.path.abspath(self.extensionPath)
        extensionName = os.path.basename(self.extensionPath)
        pathHash = hashlib.md5(cleanedPath).hexdigest()
        shortHashPath = pathHash[:6]
        return '_pm_%s_%s_%s' % (extensionName, self.moduleName, shortHashPath)

class EggPMExtension(BasePMExtension):
    """Extension class for zipped extensions"""
    def _loadClassModule(self):
        """Load the class module for this extension from the zip file"""
        sep = "/"

        # Zipped extension path:
        zippedExtensionPath = self.extensionPath
        j.logger.log("Zipped extension path: '%s'" % (zippedExtensionPath), 5)

        extensionImporter = zipimport.zipimporter(zippedExtensionPath)
        try:
            return extensionImporter.load_module(self.moduleName)
        except Exception, e:
            #Get exception type, exception instance and backtrace
            t, v, tb = sys.exc_info()
            self._handleLoadClassModuleException(t, v, tb)
