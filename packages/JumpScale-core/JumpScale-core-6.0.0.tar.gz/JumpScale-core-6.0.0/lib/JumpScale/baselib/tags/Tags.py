

from JumpScale import j
from urllib import unquote, quote

class Tags():
    """
    represent set of tags & _labels
    label is e.g. important (no value attached)
    tag is with value attached e.g. customer:kristof
    """    
    def __init__(self, tagstring='',setFunction4Tagstring=None):
        """
        @param tagstring:  example "labelexample customer:newco"
        @type tagstring: string
        @param setFunction4Tagstring is a function which will set the paramstring somewhere when changed by this class
        """
        self.tags = dict()
        self.labels = set()
        self.tagstring=tagstring
        if tagstring<>"":
            self.fromString(tagstring)
        self._setFunction4Tagstring=setFunction4Tagstring
        
    def fromString(self, tagstring):
        """
        go from string to Tag class filled in
        
        @param tagstring: example "important customer:kristof"
        @type tagstring: string        
        """
        
        if not tagstring:
            return

        if tagstring.find("'")<>-1:
            #special more complex processing required
            # r=j.codetools.regex.replace("'[\w\-_=? !]*'","","-_-",tagstring,nonRegexSubsetToReplace=" ")
            tagstring=j.codetools.regex.replace("'[\w\-_=? !]*'"," ","-|-",tagstring)
            tagstring=tagstring.replace("'","")

        tags = tagstring.split()
        for tag in tags:                
            if tag.find(':') > 0:
                key = tag.split(':')[0]
                value = tag.split(':')[1]
                self.tags[unquote(key)] = unquote(value).replace("-|-"," ")

            else:
                self.labels.add(unquote(tag))

        self.tagstring=tagstring
        
    def _toString(self):
        """
        build string representation from tags
        
        @return: string representation from tags
        @rtype: string                
        """
        labelsString = " ".join([quote(label) for label in self.labels])
        tagsString = " ".join(["%s:%s" % (quote(k), quote(v)) for k, v in self.tags.iteritems()])
        
        self.tagstring = " ".join((labelsString, tagsString)).strip()
        self.tagstring=self.tagstring.replace("%2C", ",")
        
        if self._setFunction4Tagstring<>None:
            self._setFunction4Tagstring(self.tagstring)
        
        return self.tagstring

    def getDict(self):
        r={}
        for label in self.labels:
            r["%s"%label]=True
        r.update(self.tags)
        return r

    def getValues(self,**kwargs):
        """
        for each item given as named argument check it is in the tags & and if not use it 
        e.g. args=self.getValues(id=1,name="test")
        will return a dict with id & name and these values unless if they were set in the tags already

        can further use it as follows:
        params.result=infomgr.getInfoWithHeaders(**args)

        only return the ones which are specified as args
        """
        # if kwargs.has_key("defvalue"):
        #     defvalue=kwargs["defvalue"]
        # else:
        #     defvalue=None
        result={}
        for key in kwargs.keys():
            val=kwargs[key]
            if  self.tagExists(key):
                val2=self.tagGet(key)
                if val2.find("$")<>0:
                    val=val2
            result[key]=val
        return result
            
            
        
    __repr__ = __str__ = _toString
        
    def tagGet(self, tagname, default=None):
        """
        @param tagname: e.g customer
        @type tagname: string 
        
        @return: value behind tag 
        @rtype: string
        """
        if self.tags.has_key(tagname):
            return self.tags[tagname]
        elif default is not None:
            return default
        else:
            #raise error when tag does not exist
            raise Exception('tagname %s does not exist'% tagname)
        
    def tagExists(self, tagname):
        """
        check whether tagname exists in the tags dictionary
        
        @return: true if tag exists
        @rtype: boolean        
        """
        return self.tags.has_key(tagname)
    
    def tagCheckValue(self,tagname,value):
        """
        check if specified tag is equal to value
        """
        return self.tagExists(tagname) and self.tagGet(tagname)==value
        
    def labelExists(self, labelname):
        """
        check whether labelname exists in the labels 
        
        @return: true if label exists
        @rtype: boolean        
        """
        return self.labels.issuperset(set([labelname]))
            
    
    def tagDelete(self, tagname):
        """
        delete tag, raise error if not existing
        
        @param tagname: e.g customer
        @type tagname: string        
        
        """
        if self.tags.has_key(tagname):
            val=self.tags.pop(tagname)
            self._toString()
            return val
        else:
            #raise error when tag does not exist
            raise Exception('tagname %s does not exist'% tagname)
        
    def labelDelete(self, labelname):
        """
        delete label, raise error if not existing
        
        @param labelname: e.g important
        @type labelname: string 
        """
        if not self.labelExists(labelname):
            raise Exception('label %s does not exist'% labelname)
        self.labels.remove(labelname)
        self._toString()
        
    def tagSet(self, tagName, tagValue):
        """
        add new key value tag
        
        @param tagName: e.g customer        
        @type tagName: string 
        
        @param tagValue: e.g kristof
        @type tagValue: string        
        """
        self.tags[tagName] = str(tagValue)
        self._toString()
        
    def labelSet(self, labelName):
        """
        add new label
        
        @param labelName: e.g important
        @type labelName: string
        """
        self.labels.add(labelName)
        self._toString()
        
    
    
