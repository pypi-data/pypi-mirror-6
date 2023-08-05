from JumpScale import j
from TextLineEditor import TextLineEditor
from TextCharEditor import TextCharEditor

        
class TextFileEditor:
    """
    Allow manipulate of a text file
    ideal to manipulate e.g. config files
    BE CAREFULL, CHANGES ON textfileeditor and chareditor can overwrite each other
    """
    def __init__(self,filepath):
        self.filepath=filepath
        self.content=j.system.fs.fileGetContents(filepath)
        
    def getTextLineEditor(self):
        """
        """
        return TextLineEditor(self.content,self.filepath)
    
    def getTextCharEditor(self):        
        te=TextCharEditor(self.content,self)
        self._textCharEditorActive=True
        return te
    
    def existsLine(self,pattern):
        """
        return True if pattern found (regex) False if not
        """
        if not self.content:
            return False        
        return j.codetools.regex.findOne(pattern,self.content)<>""
                
    
    def find1Line(self,includes="",excludes=""):
        """
        if moren than 1 line or 0 line error will be raised
        @param includes are include patters (regular expressions)
        @param excludes
        @return [linenr,line]
        """
        j.logger.log("try to find 1 line which matches the specified includes %s & excludes %s" % (includes,excludes),8)
        result=[]
        linenr=0
        if includes=="":
            includes=[".*"]  #match all
        if excludes=="":
            excludes=[]  #match none
        for line in self.content.split("\n"):
            if j.codetools.regex.matchMultiple(includes,line) and not j.codetools.regex.matchMultiple(excludes,line):
                result.append(line)
                linenrfound=linenr
                linefound=line
            linenr+=1
            
        if len(result)==0:
            raise RuntimeError("Could not find a line matching %s and not matching %s in file %s" % (includes,excludes,self.filepath))
        if len(result)>1:
            raise RuntimeError("Found more than 1 line matching %s" % (patterns,self.filepath))
        return [linenrfound,linefound]
    
    def replaceLinesFromFunction(self,replaceFunction,argument,includes="",excludes=""):
        """
        includes happens first
        excludes last
        both are arrays
        @param argument which is going to be give to replacefunction
        @replaceFunction is the replace function has 2 params, argument & the matching line, returns the processed line
        replace the matched line with line being processed by the functionreplaceFunction(argument,lineWhichMatches)
        
        """   
        #@todo add good logging statements everywhere   (id:49)
        self.content=j.codetools.regex.replaceLines(replaceFunction,argument, self.content,includes,excludes)
        self.save()

    def replace1LineFromFunction(self,replaceFunction,argument,includes="",excludes=""):
        """
        same as with replaceLinesFromFunction, but only 1 line will be matched
        
        """   
        self.find1Line(includes,excludes) #make sure only 1 line can match otherwise error will be raised
        self.replaceLinesFromFunction(replaceFunction,argument,includes,excludes)      
        self.save()

    def replace1Line(self,newcontent,includes="",excludes=""):
        """
        includes happens first
        excludes last
        both are arrays
        replace matching lines with new content
        """
        self.find1Line(includes,excludes) #make sure only 1 line can match otherwise error will be raised
        self.replaceLines(newcontent,includes,excludes)               
        self.save()
        
        
    def replaceLines(self,newcontent,includes="",excludes=""):
        """
        includes happens first (is regex!!!!)
        excludes last
        both are arrays
        replace matching lines with new content
        """
        def replfunc(newline,line):
            return newcontent
        self.replaceLinesFromFunction(replfunc,newcontent,includes,excludes)                    
        self.save()

    def deleteLines(self,pattern):
        """
        remove lines which match the pattern (regex) (only 1 pattern)
        """
        self.content=j.codetools.regex.removeLines(pattern,self.content)
        self.save()
        
    def appendReplaceLine(self,pattern,line):
        """
        find line which match the pattern (regex) (only 1 pattern) and then change
        if not found append to end of file
        """
        if not self.existsLine(pattern):
            self.appendLine(line)
        else:
            self.replace1Line(line,[pattern])
        
        
    def appendLine(self,line):
        if not self.content:
            self.content = "%s" % line
        else:
            if self.content[-1]<>"\n":
                self.content+="\n"
            self.content+="%s" %line
            if self.content[-1]<>"\n":
                self.content+="\n"

    def setSection(self,sectionName,content):
        """
        look for section starting with ### $sectionName
        end of section starts with ###END $sectionName
        whatever inbetween will be replaced by content

        if section does not exist yet then it will be added at end of file

        """

        lineEditor=self.getTextLineEditor()
        lineEditor.matchBlocks("main",["### %s"%sectionName],[],["###END %s"%sectionName],[])

        if not lineEditor.existsBlock("main"):
            lineEditor.addBlock("main","### %s\n\n###END %s\n"%(sectionName,sectionName))

        lineEditor.replaceBlock("main","### %s\n%s\n###END %s\n"%(sectionName,content.rstrip(),sectionName))

        lineEditor.save()
        

    def replace(self,regexFind,regexFindsubsetToReplace,replaceWith):
        """
        Search for regexFind in text and if found, replace the subset regexFindsubsetToReplace of regexFind with replacewith and returns the new text
        Example:
            replace("Q-Layer Server", "Server", "Computer", "This is a Q-Layer Server")
            will return "This is a Q-Layer Computer"
        @param regexFind: String to search for, can be a regular expression
        @param regexFindsubsetToReplace: The subset within regexFind that you want to replace
        @param replacewith: The replacement
        """        
        self.content=j.codetools.regex.replace(regexFind,regexFindsubsetToReplace,replaceWith,self.content)
        self.save()
                
    def replaceNonRegex(self,tofind,replaceWith):
        self.content=self.content.replace(tofind,replaceWith)
        self.save()

    def addItemToFoundLineOnlyOnce(self,tofind,add,ignoreRegex=None,reset=False):
        """
        look for tofind and only one add $add to it,
        will not do this on lines matching the regexes
        @param reset if True, will remove the regex first, means will always be added
        
        """        
        out=""
        done=False
        for line in self.content.split("\n"):
            if reset  and done==False and line.find(tofind)<>-1 and ignoreRegex<>None:
                #found right line
                line=j.codetools.regex.replace(ignoreRegex, ignoreRegex, "", line).rstrip()
                line=line+add
                print "CH:%s" % line
                done=True
            if done==False and line.find(tofind)<>-1 and  \
               (ignoreRegex<>None and not j.codetools.regex.match(ignoreRegex,line)):
                #found line we can change
                line=line.replace(tofind,tofind+add)
                done=True
            out+="%s\n"%line
        self.content=out  
        self.save()
            
        
    def getRegexMatches(self, pattern):
        result= j.codetools.regex.getRegexMatches(pattern, self.content)
        return result
            
    def save(self,filepath=None):
        """
        write the manipulated file to a new path or to the original
        """
        if filepath==None:
            filepath=self.filepath
        if filepath==None:
            raise RuntimeError("Cannot write the textfile because path is None")
        j.system.fs.writeFile(filepath,self.content)            
        



