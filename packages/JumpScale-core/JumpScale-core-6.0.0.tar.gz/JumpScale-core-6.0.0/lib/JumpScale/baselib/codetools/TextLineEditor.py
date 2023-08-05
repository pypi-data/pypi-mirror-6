
from JumpScale import j

#@todo P2 S4 :eduard TextLineEditor tool does not work any more, is a pitty because ideal to parse config files on a filesystem (id:83)

class TextLineEditor():
    """
    represents a piece of text but broken appart in blocks/tokens
    this one works on a line basis
    """
    
    def __init__(self,text,path):
        self.lines=[]
        self._higestblocknr={} #key is name of block, the value is the last used blocknr
        self.path=path
        for line in text.split("\n"):
            self.lines.append(LTLine(line))
        
    def getNrLines(self):
        return len(self.lines)
        
    def existsBlock(self,blockname):
        return self._higestblocknr.has_key(blockname)
    
    def getBlockNames(self):
        return self._higestblocknr.keys()
    
    def matchBlocks(self,blockname,blockStartPatterns=['.*'],blockStartPatternsNegative=[],blockStopPatterns=[],blockStopPatternsNegative=[],blockfilter=""):
        """
        walk over blocks which are marked as matched and split blocks in more blocks depending criteria
        can be usefull to do this multiple times (sort of iterative) e.g. find class and then in class remove comments
        @param blockfilter will always match beginning of blockname e.g. can use userauth.sites  then change userauth.sites  will match all sites
        look for blocks starting with line which matches one of patterns in blockStartPatterns and not matching one of patterns in blockStartPatternsNegative
        block will stop when line found which matches one of patterns in blockStopPatterns and not in blockStopPatternsNegative or when next match for start is found
        example pattern: '^class ' looks for class at beginning of line with space behind 

        """

        #check types of input
        if type(blockStartPatterns).__name__<>'list' or type(blockStartPatternsNegative).__name__<>'list' or type(blockStopPatterns).__name__<>'list' \
            or type(blockStopPatternsNegative).__name__<>'list':
            raise RuntimeError("Blockstartpatterns,blockStartPatternsNegative,blockStopPatterns,blockStopPatternsNegative has to be of type list")
                                          
        state="scan"
        lines=self.lines
        line=""
        for t in range(len(lines)):
            lineObject=lines[t]            
            line=lineObject.line
            # print "\nPROCESS: %s,%s state:%s line:%s" % (t,len(lines)-1,state,line)
            emptyLine = line.strip()==""

            if t==len(lines)-1 :
                #end of file
                if state=="foundblock": #still in found block so add the last line
                    self._processLine(lineObject,blockname)  #add last line
                return

            if state=="foundblock" and j.codetools.regex.matchMultiple(blockStopPatterns,line) and not j.codetools.regex.matchMultiple(blockStopPatternsNegative,line):
                #found end of block
                state="scan" #can continue to scan for next line
                self._processLine(lineObject,blockname)
                continue                

            if state=="foundblock": #still in found block so add the last line
                self._processLine(lineObject,blockname)  #add last line                            

            if j.codetools.regex.matchMultiple(blockStartPatterns,line) and not j.codetools.regex.matchMultiple(blockStartPatternsNegative,line):
                #found beginning of block
                state="foundblock"
                self._processLine(lineObject,blockname,next=True)


    def _processLine(self,lineObject,blockname,next=False):
        if lineObject.block==blockname:
            j.errorconditionhandler.raiseBug(message="Cannot find block with name %s in block which has already same name"%blo,category="lineeditor")
        lineObject.block=blockname
        if next:
            lineObject.blocknr=self.getNextBlockNr(blockname)
        else:
            lineObject.blocknr=self.getHighestBlockNr(blockname)

    def getNextBlockNr(self,name):
        if not self._higestblocknr.has_key(name):
            self._higestblocknr[name]=1
        else:
            self._higestblocknr[name]+=1
        return self._higestblocknr[name]

    def getHighestBlockNr(self,name):
        if not self._higestblocknr.has_key(name):
            raise RuntimeError("Cound not find block with name %s" % name)
        else:
            return self._higestblocknr[name]
    
    def appendBlock(self,text,blockname=""):
        """
        @param match means block was found and matching
        """
        blocknr=self.getNextBlockNr(blockname)
        for line in text.split("\n"):
            self.lines.append(LTLine(line,blockname,blocknr))
        
    def insertBlock(self,linenr,text,blockname="",blocknr=None):
        """
        block will be inserted at linenr, means line with linenr will be moved backwards
        """
        if blocknr==None:
            blocknr=self.getNextBlockNr(blockname)
        for line in text.split("\n").revert():
            self.lines.insert(linenr,LTLine(line,blockname,blocknr))            
            
    def deleteBlock(self,blockname,blocknr=None):
        """
        mark block as not matching based on startline
        """
        self.getBlock(blockname,blocknr) #just to check if block exists
        self.lines=[line for line in self.lines if (line.name<>blockname and (blocknr==None or line.blocknr==blocknr))]
        
        
    def getBlock(self,blockname,blocknr):
        """
        get block based on startline
        """
        block=[line for line in self.lines (line.name==blockname and line.blocknr==blocknr)]
        if len(block)==0:
            raise RuntimeError("Cannot find block from text with blockname %s and blocknr %s" % (blockname,blocknr))
        return str.join(block)
        
    def replaceBlock(self,blockname,text,blocknr=1):
        """
        set block based on startline with new content
        """
        if text[-1]<>"\n":
            text+="\n"
        state="scan"
        lastBlockNameNr=""
        linenr=0
        nrlines=len(self.lines)
        x=0
        lastx=0
        while True:
            if x>nrlines-1:
                break
            line=self.lines[x]
            # print "%s %s"%(x,line)            
            if line.block==blockname and line.blocknr==blocknr:
                state="found"
                lastBlockNameNr="%s_%s"%(line.block,line.blocknr)
                self.lines.pop(x)
                x=x-1
                nrlines=len(self.lines)
                lastx=x

            if state=="found" and lastBlockNameNr<>lastBlockNameNr:
                #end of block
                break

            x=x+1

        self.lines.append(None)

        x=lastx+1
        text=text.rstrip()
        for line in text.split("\n"):
            self.lines.insert(x,LTLine(line,blockname,blocknr))
            x+=1

        self.lines=self.lines[:-1]        

    def save(self):
        txt="\n".join([item.line for item in self.lines])
        
        j.system.fs.writeFile(filename=self.path,contents=txt)
        
    def getFirstLineNrForBlock(self,blockname,blocknr):
        for linenr in range(len(self.lines)):
            line=self.lines[linenr]
            if line.name==blockname and line.blocknr==blocknr:
                return linenr
        raise RuntimeError("Could not find block with name %s and blocknr %s" % (blockname,blocknr))
    
       
    def addBlock(self,blockname,text):
        first=True
        for line in text.split("\n"):
            if first:
                self.lines.append(LTLine(line,blockname,self.getNextBlockNr(blockname)))
                first=False
            else:
                self.lines.append(LTLine(line,blockname,self.getHighestBlockNr(blockname)))
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        if len(self.lines)>0:
            return "".join([str(block) for block in self.lines])
        else:
            return ""

class LTLine():
    def __init__(self,line,blockname="",blocknr=0):
        """        
        @param no blockname means ignore
        """
        self.block=blockname
        self.line=line
        self.blocknr=blocknr
     
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        if self.block<>"":
            text="+ %s %s: %s\n" % (self.block,self.blocknr,self.line)
            return text
        else:
            text="- %s\n" % (self.line)
            return text
        
        

