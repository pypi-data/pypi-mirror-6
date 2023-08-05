from JumpScale import j
import struct
try:
    from REGEXTOOL import *
except:
    pass

from .FS import *

class FSWalkerStats():
    def __init__(self):
        self.start=j.base.time.getTimeEpoch()
        self.stop=0
        self.sizeUncompressed={}

        self.sizeCompressed={}
        self.nr={}
        self.duplicate={}

        for i in ["D","F","L"]:
            self.registerType(i)
            
        self.sizeUncompressedTotal=0
        self.sizeCompressedTotal=0
        self.nrTotal=0
        self.duplicateTotal=0

    def registerType(self,ttype):
        if not self.sizeUncompressed.has_key(ttype):
            self.sizeUncompressed[ttype]=0
        if not self.sizeCompressed.has_key(ttype):
            self.sizeCompressed[ttype]=0
        if not self.nr.has_key(ttype):
            self.nr[ttype]=0
        if not self.duplicate.has_key(ttype):
            self.duplicate[ttype]=0

    def callstop(self):
        self.stop=j.base.time.getTimeEpoch()
        self._getTotals()

    def _getTotals(self):
        sizeUncompressed=0
        for key in self.sizeUncompressed.keys():
            sizeUncompressed+=self.sizeUncompressed[key]
        self.sizeUncompressedTotal=sizeUncompressed
        
        sizeCompressed=0
        for key in self.sizeCompressed.keys():
            sizeCompressed+=self.sizeCompressed[key]
        self.sizeCompressedTotal=sizeCompressed
        
        nr=0
        for key in self.nr.keys():
            nr+=self.nr[key]
        self.nrTotal=nr

        duplicate=0
        for key in self.duplicate.keys():
            duplicate+=self.duplicate[key]
        self.duplicateTotal=duplicate

    def add2stat(self,ttype="F",sizeUncompressed=0,sizeCompressed=0,duplicate=False):
        self.sizeUncompressed[ttype]+=sizeUncompressed
        self.sizeCompressed[ttype]+=sizeCompressed
        self.nr[ttype]+=1
        if duplicate:
            self.duplicate[ttype]+=1

    def __repr__(self):
        self.callstop()
        duration=self.stop-self.start
        out="nrsecs:%s"%duration
        out="nrfiles:%s\n"%self.nrTotal
        out+="nrfilesDuplicate:%s\n"%self.duplicateTotal
        sizeUncompressedTotal=(float(self.sizeUncompressedTotal)/1024/1024)
        out+="size uncompressed:%s\n"%sizeUncompressedTotal
        sizeCompressedTotal=(float(self.sizeCompressedTotal)/1024/1024)
        out+="size compressed:%s\n"%sizeCompressedTotal
        out+="uncompressed send per sec in MB/sec: %s"% round(sizeUncompressedTotal/duration,2)
        out+="compressed send per sec in MB/sec: %s"% round(sizeCompressedTotal/duration,2)

    __str__=__repr__

class LocalFS():

    def abspath(self,path):
        return os.path.abspath(path)

    def isFile(self,path,followlinks=True):
        return j.system.fs.isFile(path,followlinks)

    def isDir(self,path,followlinks=True):
        return j.system.fs.isDir(path,followlinks)

    def isLink(self,path,junction=True):
        return j.system.fs.isLink(path,junction)

    def stat(self,path):
        return os.stat(path)

    def lstat(self,path):
        return os.lstat(path)

    def list(self,path):
        return j.base.fs.list(path)



class FSWalker():

    def __init__(self,filesystemobject=None):
        self.stats=None
        self.statsStart()
        self.statsNr=0
        self.statsSize=0
        self.lastPath=""
        if filesystemobject==None:
            self.fs=LocalFS()
        else:
            self.fs=filesystemobject()
       
    def log(self,msg):
        print(msg)

    def statsStart(self):
        self.stats=FSWalkerStats()

    def statsPrint(self): 
        print("lastpath:%s"%self.lastPath)
        try:
            print(str(self.stats))
        except:
            print('None')

    def statsAdd(self,path="",ttype="F",sizeUncompressed=0,sizeCompressed=0,duplicate=False):
        self.stats.add2stat(ttype=ttype,sizeUncompressed=sizeUncompressed,sizeCompressed=sizeCompressed,duplicate=duplicate)
        self.statsNr+=1
        self.statsSize+=sizeUncompressed
        self.lastPath=path
        if self.statsNr>2000 or self.statsSize>100000000:
            self.statsPrint()
            self.statsNr=0
            self.statsSize=0
    
    def _findhelper(self,arg,path):
        arg.append(path)
    
    def find(self,root, includeFolders=False,includeLinks=False, pathRegexIncludes={},pathRegexExcludes={},followlinks=False,\
        childrenRegexExcludes=[".*/log/.*","/dev/.*","/proc/.*"],mdserverclient=None):
        """
        @return {files:[],dirs:[],links:[],...$othertypes}
        """

        result={}
        result["F"]=[]
        result["D"]=[]
        result["L"]=[]

        def processfile(path,stat,arg):
            result["F"].append([path,stat])    

        def processdir(path,stat,arg):
            result["D"].append([path,stat])    

        def processlink(src,dest,stat,arg):
            result["L"].append([src,dest,stat])   

        def processother(path,stat,type,arg):
            if result.has_key(type):
                result[type]=[]
            result[type].append([path,stat])  

        callbackFunctions={}
        callbackFunctions["F"]=processfile
        callbackFunctions["D"]=processdir
        callbackFunctions["L"]=processlink
        callbackFunctions["O"]=processother  #type O is a generic callback which matches all not specified (will not match F,D,L)

        callbackMatchFunctions=self.getCallBackMatchFunctions(pathRegexIncludes,pathRegexExcludes,includeFolders=includeFolders,includeLinks=includeLinks)

        root = os.path.abspath(root)
        self.walk(root,callbackFunctions,arg={},callbackMatchFunctions=callbackMatchFunctions,childrenRegexExcludes=childrenRegexExcludes,\
            pathRegexIncludes=pathRegexIncludes,pathRegexExcludes=pathRegexExcludes,mdserverclient=mdserverclient)

        return result

    def getCallBackMatchFunctions(self,pathRegexIncludes={},pathRegexExcludes={},includeFolders=True,includeLinks=True):

        C="""        
if pathRegexIncludes.has_key("$type") and not pathRegexExcludes.has_key("$type"):
    def matchobj$type(path,arg,pathRegexIncludes,pathRegexExcludes):
        return REGEXTOOL.matchPath(path,pathRegexIncludes["$type"],[])
elif not pathRegexIncludes.has_key("$type") and pathRegexExcludes.has_key("$type"):
    def matchobj$type(path,arg,pathRegexIncludes,pathRegexExcludes):
        return REGEXTOOL.matchPath(path,[],pathRegexExcludes["$type"])
elif pathRegexIncludes.has_key("$type") and pathRegexExcludes.has_key("$type"):
    def matchobj$type(path,arg,pathRegexIncludes,pathRegexExcludes):
        return REGEXTOOL.matchPath(path,pathRegexIncludes["$type"],pathRegexExcludes["$type"])
else:
    matchobj$type=None
"""       
        for ttype in ["F","D","L"]:
            C2=C.replace("$type",ttype)
            exec(C2)

        callbackMatchFunctions={}
        if matchobjF!=None and (pathRegexIncludes.has_key("F") or pathRegexExcludes.has_key("F")):
            callbackMatchFunctions["F"]=matchobjF
        if includeFolders:
            if matchobjD!=None and (pathRegexIncludes.has_key("D") or pathRegexExcludes.has_key("D")):
                callbackMatchFunctions["D"]=matchobjD
        if includeLinks:
            if matchobjL!=None and (pathRegexIncludes.has_key("L") or pathRegexExcludes.has_key("L")):
                callbackMatchFunctions["L"]=matchobjL
        if pathRegexIncludes.has_key("O") or pathRegexExcludes.has_key("O"):
            callbackMatchFunctions["O"]=matchobjO

        return callbackMatchFunctions
          
    def walk(self,root,callbackFunctions={},arg=None,callbackMatchFunctions={},followlinks=False,\
        childrenRegexExcludes=[".*/log/.*","/dev/.*","/proc/.*"],pathRegexIncludes={},pathRegexExcludes={},mdserverclient=None):
        '''

        Walk through filesystem and execute a method per file and dirname if the match function selected the item

        Walk through all files and folders and other objects starting at root, 
        recursive by default, calling a given callback with a provided argument and file
        path for every file & dir we could find.

        To match the function use the callbackMatchFunctions  which are separate for all types of objects (Dir=D, File=F, Link=L)
        when it returns True the path will be further processed

        Examples
        ========
        >>> def my_print(path,arg):
        ...     print arg+path
        ...

        >>> def match(path,arg):
        ...     return True #means will process the object e.g. file which means call my_print in this example
        ...

        >>> self.walk('/foo', my_print,arg="Test: ", callbackMatchFunctions=match)
        test: /foo/file1
        test: /foo/file2
        test: /foo/file3
        test: /foo/bar/file4

        @param root: Filesystem root to crawl (string)
        
        '''
        #We want to work with full paths, even if a non-absolute path is provided
        root = os.path.abspath(root)
        if not self.fs.isDir(root):
            raise ValueError('Root path for walk should be a folder')
        
        # print "ROOT OF WALKER:%s"%root
        if mdserverclient==None:
            self._walkFunctional(root,callbackFunctions, arg,callbackMatchFunctions,followlinks,\
                childrenRegexExcludes=childrenRegexExcludes,pathRegexIncludes=pathRegexIncludes,pathRegexExcludes=pathRegexExcludes)
        else:
            self._walkFunctionalMDS(root,callbackFunctions, arg,callbackMatchFunctions,followlinks,\
                childrenRegexExcludes=childrenRegexExcludes,pathRegexIncludes=pathRegexIncludes,pathRegexExcludes=pathRegexExcludes)

    def _walkFunctional(self,root,callbackFunctions={},arg=None,callbackMatchFunctions={},followlinks=False,\
        childrenRegexExcludes=[],pathRegexIncludes={},pathRegexExcludes={}):

        paths=self.fs.list(root)
        for path2 in paths:
            self.log("walker path:%s"% path2)
            if self.fs.isFile(path2):
                ttype="F"
            elif self.fs.isLink(path2):
                ttype="L"   
            elif self.fs.isDir(path2,followlinks):
                ttype="D"
            else:
                raise RuntimeError("Can only detect files, dirs, links")

            if not callbackMatchFunctions.has_key(ttype) or (callbackMatchFunctions.has_key(ttype) and callbackMatchFunctions[ttype](path2,arg,pathRegexIncludes,pathRegexExcludes)):
                self.log("walker filepath:%s"% path2)                
                self.statsAdd(path=path2,ttype=ttype,sizeUncompressed=0,sizeCompressed=0,duplicate=False)

                if callbackFunctions.has_key(ttype):
                    if ttype in "DF":
                        stat=self.fs.stat(path2)
                        statb=struct.pack("<IHHII",stat.st_mode,stat.st_gid,stat.st_uid,stat.st_size,stat.st_mtime)
                        callbackFunctions[ttype](path=path2,stat=statb,arg=arg)
                    else:
                        stat=self.fs.lstat(path2)
                        statb=struct.pack("<IHHII",stat.st_mode,stat.st_gid,stat.st_uid,stat.st_size,stat.st_mtime)
                        callbackFunctions[ttype](src=path2,dest=os.path.realpath(path2),arg=arg,stat=statb)

            if ttype=="D":
                if REGEXTOOL.matchPath(path2,pathRegexIncludes.get(ttype,[]) ,childrenRegexExcludes):
                    self._walkFunctional(path2,callbackFunctions, arg,callbackMatchFunctions,followlinks,\
                        childrenRegexExcludes=childrenRegexExcludes,pathRegexIncludes=pathRegexIncludes,pathRegexExcludes=pathRegexExcludes)
        

class FSWalkerFactory():
    def get(self,filesystemobject=None):
        return FSWalker(filesystemobject=filesystemobject)

j.base.fswalker=FSWalkerFactory()


