

import os
import os.path
from JumpScale import j

class FSWalker:
    
    @staticmethod
    def _checkDepth(path,depths,root=""):
        if depths==[]:
            return True
        #path=j.system.fs.pathclean(path)
        path=j.system.fs.pathRemoveDirPart(path,root)
        for depth in depths:
            dname=os.path.dirname(path)
            split=dname.split(os.sep)
            split = [ item for item in split if item<>""]
            #print split
            if depth==len(split):
                return True
        else:
            return False
    
    @staticmethod    
    def _checkContent(path,contentRegexIncludes=[], contentRegexExcludes=[]):
        if contentRegexIncludes==[] and contentRegexExcludes==[]:
            return True
        content=j.system.fs.fileGetContents(path)
        if j.codetools.regex.matchMultiple(patterns=contentRegexIncludes,text=content) and not j.codetools.regex.matchMultiple(patterns=contentRegexExcludes,text=content):
            return True
        return False

    @staticmethod       
    def _findhelper(arg,path):
        arg.append(path)
    
    @staticmethod    
    def find(root, recursive=True, includeFolders=False, pathRegexIncludes=[".*"],pathRegexExcludes=[], contentRegexIncludes=[], contentRegexExcludes=[],depths=[]):
        listfiles=[]
        FSWalker.walk(root, FSWalker._findhelper, listfiles, recursive, includeFolders, pathRegexIncludes,pathRegexExcludes, contentRegexIncludes, contentRegexExcludes,depths)
        return listfiles
    
    @staticmethod
    def walk(root, callback, arg="", recursive=True, includeFolders=False, \
        pathRegexIncludes=[".*"],pathRegexExcludes=[], contentRegexIncludes=[], contentRegexExcludes=[],\
        depths=[],followlinks=True):
        '''Walk through filesystem and execute a method per file

        Walk through all files and folders starting at C{root}, recursive by
        default, calling a given callback with a provided argument and file
        path for every file we could find.

        If C{includeFolders} is True, the callback will be called for every
        folder we found as well.

        Examples
        ========
        >>> def my_print(arg, path):
        ...     print arg, path
        ...
        >>> FSWalker.walk('/foo', my_print, 'test:')
        test: /foo/file1
        test: /foo/file2
        test: /foo/file3
        test: /foo/bar/file4

        return False if you want recursion to stop (means don't go deeper)

        >>> def dirlister(arg, path):
        ...     print 'Found', path
        ...     arg.append(path)
        ...
        >>> paths = list()
        >>> FSWalker.walk('/foo', dirlister, paths, recursive=False, includeFolders=True)
        /foo/file1
        /foo/file2
        /foo/file3
        /foo/bar
        >>> print paths
        ['/foo/file1', '/foo/file2', '/foo/file3', '/foo/bar']

        @param root: Filesystem root to crawl (string)
        @param callback: Callable to call for every file found, func(arg, path) (callable)
        @param arg: First argument to pass to callback
        @param recursive: Walk recursive or not (bool)
        @param includeFolders: Whether to call C{callable} for folders as well (bool)
        @param pathRegexIncludes / Excludes  match paths to array of regex expressions (array(strings))
        @param contentRegexIncludes / Excludes match content of files to array of regex expressions (array(strings))
        @param depths array of depth values e.g. only return depth 0 & 1 (would mean first dir depth and then 1 more deep) (array(int)) 
        
        '''
        if not j.system.fs.isDir(root):
            raise ValueError('Root path for walk should be a folder')
        if recursive==False:
            depths=[0]
        #We want to work with full paths, even if a non-absolute path is provided
        root = os.path.abspath(root)

        # print "ROOT OF WALKER:%s"%root

        j.system.fswalker._walk(root,callback,arg, includeFolders, pathRegexIncludes,pathRegexExcludes,\
            contentRegexIncludes, contentRegexExcludes, depths,followlinks)

        # #if recursive:
        # for dirpath, dirnames, filenames in os.walk(root,followlinks=followlinks):
        #     #Folders first
        #     if includeFolders:
        #         for dirname in dirnames:
        #             path = os.path.join(dirpath, dirname)
        #             if j.codetools.regex.matchMultiple(patterns=pathRegexIncludes,text=path) and \
        #                     not j.codetools.regex.matchMultiple(patterns=pathRegexExcludes,text=path):
        #                 if FSWalker._checkDepth(path,depths,root) and \
        #                         FSWalker._checkContent(path,contentRegexIncludes, contentRegexExcludes):
        #                     result=callback(arg, path)
        #     for filename in filenames:
        #         path = os.path.join(dirpath, filename)
        #         if j.codetools.regex.matchMultiple(patterns=pathRegexIncludes,text=path) and not j.codetools.regex.matchMultiple(patterns=pathRegexExcludes,text=path):
        #             if FSWalker._checkDepth(path,depths,root) and FSWalker._checkContent(path,contentRegexIncludes, contentRegexExcludes):
        #                 callback(arg, path)
                

    @staticmethod
    def _walk(path, callback, arg="", includeFolders=False, \
        pathRegexIncludes=[".*"],pathRegexExcludes=[], contentRegexIncludes=[], contentRegexExcludes=[],\
        depths=[],followlinks=True):
        for path2 in j.system.fs.listFilesAndDirsInDir(path):
            if j.system.fs.isDir(path2, followlinks):
                if includeFolders:
                    result=True
                    if j.codetools.regex.matchMultiple(patterns=pathRegexIncludes,text=path2) and \
                            not j.codetools.regex.matchMultiple(patterns=pathRegexExcludes,text=path2):
                        if FSWalker._checkDepth(path2,depths,path) and \
                                FSWalker._checkContent(path2,contentRegexIncludes, contentRegexExcludes):
                            result=callback(arg, path2)
                    if result==False:
                        continue #do not recurse go to next dir
                #recurse
                j.system.fswalker._walk(path2,callback,arg, includeFolders, pathRegexIncludes,pathRegexExcludes,\
                        contentRegexIncludes, contentRegexExcludes, depths,followlinks)
        
            if j.system.fs.isFile(path2, followlinks):
                if j.codetools.regex.matchMultiple(patterns=pathRegexIncludes,text=path2) and not j.codetools.regex.matchMultiple(patterns=pathRegexExcludes,text=path):
                    if FSWalker._checkDepth(path2,depths,path) and FSWalker._checkContent(path2,contentRegexIncludes, contentRegexExcludes):
                        callback(arg, path2)



    @staticmethod
    def walkFunctional(root,callbackFunctionFile=None, callbackFunctionDir=None,arg="", \
        callbackForMatchDir=None,callbackForMatchFile=None):
        '''Walk through filesystem and execute a method per file and dirname

        Walk through all files and folders starting at C{root}, recursive by
        default, calling a given callback with a provided argument and file
        path for every file & dir we could find.

        To match the function use the callbackForMatch function which are separate for dir or file
        when it returns True the path will be further processed
        when None (function not given match will not be done)

        Examples
        ========
        >>> def my_print(path,arg):
        ...     print arg, path
        ...
        #if return False for callbackFunctionDir then recurse will not happen for that dir

        >>> def matchDirOrFile(path,arg):
        ...     return True #means will match all
        ...

        >>> FSWalker.walkFunctional('/foo', my_print,my_print, 'test:',matchDirOrFile,matchDirOrFile)
        test: /foo/file1
        test: /foo/file2
        test: /foo/file3
        test: /foo/bar/file4

        @param root: Filesystem root to crawl (string)
        #@todo complete
        
        '''
        #We want to work with full paths, even if a non-absolute path is provided
        root = os.path.abspath(root)

        if not j.system.fs.isDir(root):
            raise ValueError('Root path for walk should be a folder')
        
        # print "ROOT OF WALKER:%s"%root

        j.system.fswalker._walkFunctional(root,callbackFunctionFile, callbackFunctionDir,arg, callbackForMatchDir,callbackForMatchFile)

    @staticmethod
    def _walkFunctional(path,callbackFunctionFile=None, callbackFunctionDir=None,arg="", callbackForMatchDir=None,callbackForMatchFile=None):
        for path2 in j.system.fs.listFilesAndDirsInDir(path):
            # print "walker path:%s"% path2
            if j.system.fs.isDir(path2, True):
                # print "walker dirpath:%s"% path2
                if callbackForMatchDir==None or callbackForMatchDir(path2,arg):
                    #recurse
                    # print "walker matchdir:%s"% path2
                    if callbackFunctionDir==None:
                        j.system.fswalker._walkFunctional(path2,callbackFunctionFile, callbackFunctionDir,arg, callbackForMatchDir,callbackForMatchFile)
                    else:
                        result=callbackFunctionDir(path2,arg)
                        if result<>False:
                            # print "walker recurse:%s"% path2
                            j.system.fswalker._walkFunctional(path2,callbackFunctionFile, callbackFunctionDir,arg, callbackForMatchDir,callbackForMatchFile)
        
            if j.system.fs.isFile(path2, True):
                # print "walker filepath:%s"% path2
                if callbackForMatchFile==False:
                    continue
                if callbackForMatchFile==None or callbackForMatchFile(path2,arg):
                    #execute 
                    callbackFunctionFile(path2,arg)


