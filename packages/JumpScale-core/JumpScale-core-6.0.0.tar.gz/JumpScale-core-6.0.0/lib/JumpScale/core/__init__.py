
from JumpScale import j

import os

def _setup_stacktrace_hook():
    '''Set up SIGUSR2 signal handler which dumps stack traces of all threads'''
    try:
        import signal
    except ImportError:
        # No signal support on current platform, ignore
        return

    sig = signal.SIGUSR2

    def stderr():
        '''Coroutine which writes input to sys.stderr and a dump file,
        /tmp/pm_<PID>.stack'''
        outputs = list()

        try:
            import sys
            outputs.append((sys.stderr.write, sys.stderr.flush, lambda: None, ))
        except Exception:
            pass

        try:
            import os
            name = '/tmp/pm_%d.stack' % os.getpid()
            fd = open(name, 'w')
            outputs.append((fd.write, fd.flush, fd.close, ))
        except Exception:
            pass

        try:
            while True:
                message = yield

                if message is None:
                    break

                for write, flush, _ in outputs:
                    try:
                        write(message)
                        flush()
                    except Exception:
                        pass
        finally:
            for _, _, close in outputs:
                try:
                    close()
                except Exception:
                    pass

    def getframes(output, frame):
        '''Get a list of all current frames

        This function tries to use sys._current_frames to get a list of the
        frames of every running thread and their thread ID. If this function is
        not available, the given frame will be returned using the string
        '<unknown>' as thread ID.
        '''
        if j.application.skipTraceback:
            return None
        import sys

        # Using sys._current_frames for now
        # We could rewrite this using ctypes as well, see the implementation of
        # _PyThread_CurrentFrames at
        # http://svn.python.org/projects/python/trunk/Python/pystate.c
        current_frames = getattr(sys, '_current_frames', None)
        if not current_frames:
            output('Your system has no support to dump stacks of all threads\n')
            output('Only dumping interrupted frame\n')
            return (('<current>', frame, ), )
        else:
            return tuple(current_frames().items())

    def dump_proc_status(output):
        import os.path

        procfile = '/proc/%d/status' % os.getpid()

        if not os.path.exists(procfile):
            # File doesn't exist, we're not running on Linux or something alike
            return

        try:
            fd = open(procfile, 'r')
        except Exception:
            # No permissions or something alike?
            # Funny if a process would have no permission on its own status proc
            # file, but anyway, better safe than sorry
            return

        try:
            data = fd.read()
        finally:
            fd.close()

        output('Dumping content of %s\n' % procfile)
        output('\n')
        output(data)
        output('\n')

    def handler_impl(output, num, frame):
        '''Implementation of the signal handler

        This will be called inside a try/except clause so the signal handler
        behaves correctly.
        '''
        import traceback

        output('Got signal %s\n' % str(num))
        output('Dumping current stack frame(s)\n')
        frames = getframes(output, frame)
        output('\n')

        try:
            from threading import _active as active_threads
        except ImportError:
            active_threads = dict()

        for threadid, frame in frames:
            title = None
            if threadid in active_threads:
                try:
                    name = active_threads[threadid].getName()
                except Exception:
                    pass
                else:
                    if name:
                        title = 'Thread %s (%s)' % (name, str(threadid))

            if not title:
                title = 'Thread %s' % str(threadid)

            output('%s\n%s\n' % (title, '=' * len(title)))

            try:
                import thread
                get_ident = thread.get_ident
            except (ImportError, AttributeError):
                get_ident = lambda: object()

            ident = get_ident()
            if threadid == get_ident():
                # We want to strip of ourself from the stacktrace
                orig_frame = frame
                while frame:
                    # If we found the frame of this 'handler' function
                    if frame.f_code == handler.func_code:
                        # Go one frame up and return
                        frame = frame.f_back
                        break

                    # Else go up one more frame
                    frame = frame.f_back

                # If we were not able to find the stackframe we were looking
                # for, just use the original one
                if not frame:
                    frame = orig_frame

            # Format and print backtrace
            stack = ''.join(traceback.format_stack(frame))
            output(stack)
            output('\n')

        try:
            dump_proc_status(output)
        except Exception:
            pass

    def handler(num, frame):
        '''Signal handler which dumps Python stacks of all running threads'''
        output = stderr()
        output.next()
        output = output.send
        try:
            handler_impl(output, num, frame)
        except Exception as e:
            output('An exception occurred while handling signal %d\n' % num)
            output('Exception information:\n')
            output('%s\n\n' % str(e))

        try:
            output(None)
        except StopIteration:
            pass

    # Install signal handler, if none set
    # Check whether a handler is set
    orig_handler = signal.getsignal(sig)
    if orig_handler != signal.SIG_DFL:
        return

    # Set up handler
    old = signal.signal(sig, handler)

# Set up our signal handler
try:
    _setup_stacktrace_hook()
except Exception as e:
    pass
# Remove the no longer needed function
del _setup_stacktrace_hook

from .Dirs import Dirs
j.dirs=Dirs()

from . import logging
from .Application import Application

from . import system

j.system.installtools=j.base.fs.installtools

from . import enumerators

j.application=Application()
from . import base
from . import baseclasses
from JumpScale.core.baseclasses.BaseEnumeration import enumerations
j.enumerators=enumerations

from PlatformTypes import PlatformTypes
j.system.platformtype=PlatformTypes()

from . import pmtypes
pmtypes.register_types()
j.basetype=pmtypes.register_types()

from . import errorhandling

# j.pm_hooked_extension_dirs = dict()

import JumpScale.baselib.platforms
import JumpScale.core.config
import JumpScale.baselib.hrd
import JumpScale.baselib.startupmanager

from . import shellconfig
from . import console
from . import gui

import JumpScale.baselib.jsdeveltools

#reinit whoAmI after dirs are loaded
j.application.initWhoAmI()


# from extensions.PMExtensions import PMExtensions

# from JumpScale.core.JumpScale import JumpScale

# class InteractiveExtensions(PMExtensionsGroup):
#     def __init__(self):
#         self._init=False
#         self.__init_properties__()
#         self.pm_name="i"
#         self.pm_location="i"

#     def _initExtensions(self):
#         if self._init==False:
#             self._pmExtensions = PMExtensions(self, 'i.', suppressAlreadyMountedError=True)
#             ##self._pmExtensions.load(j.system.fs.joinPaths(self.dirs.extensionsDir,"interactive"))
#             self._pmExtensions.load(j.system.fs.joinPaths(j.dirs.extensionsDir,"core"))
#             self._init=True

#     def extensionsLoad(self,extensionsDir):
#         self._pmExtensions.load(extensionsDir)

