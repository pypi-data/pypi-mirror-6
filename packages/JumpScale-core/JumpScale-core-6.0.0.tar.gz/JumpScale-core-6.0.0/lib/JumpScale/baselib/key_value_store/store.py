import json
#import pymodel
import time
from abc import ABCMeta, abstractmethod
from JumpScale import j
from JumpScale.core.baseclasses import BaseEnumeration


class KeyValueStoreType(BaseEnumeration):

    def __init__(self, value=None):
        self.value = value

    @classmethod
    def _initItems(cls):
        cls.registerItem('arakoon')
        cls.registerItem('file_system')
        cls.registerItem('memory')
        cls.registerItem('redis')
        cls.finishItemRegistration()


class KeyValueStoreBase(object):
    '''KeyValueStoreBase defines a store interface.'''

    __metaclass__ = ABCMeta

    def __init__(self, serializers=[]):
        #self.id = j.application.getUniqueMachineId()
        self.serializers = serializers
        self.unserializers = list(reversed(self.serializers))

    def __new__(cls, *args, **kwargs):
        '''
        Copies the doc strings (when available) from the base implementation
        '''

        attrs = cls.__dict__.iteritems()

        for attrName, attr in attrs:
            if not attr.__doc__ and\
               hasattr(KeyValueStoreBase, attrName) and\
               not attrName.startswith('_')\
            and callable(attr):

                baseAttr = getattr(KeyValueStoreBase, attrName)
                attr.__doc__ = baseAttr.__doc__

        return object.__new__(cls)

    @abstractmethod
    def get(self, category, key):
        '''
        Gets a key value pair from the store.

        @param: category of the key value pair
        @type: String

        @param: key of the key value pair
        @type: String

        @return: value of the key value pair
        @rtype: Objects
        '''
        pass

    def serialize(self,value):
        for serializer in self.serializers:
            value = serializer.dumps(value)
        return value

    def unserialize(self,value):
        for serializer in self.unserializers:
            value = serializer.loads(value)
        return value


    def cacheSet(self,key,value,expirationInSecondsFromNow=60):
        #time in minutes for expiration
        ttime=j.base.time.getTimeEpoch()
        value=[ttime+expirationInSecondsFromNow,value]
        if key=="":
            key=j.base.idgenerator.generateGUID()
        self.set("cache", key, value)
        return key
        # if nrMinutesExpiration>0:            
        #     self.set("cache", key, value)
        #     tt=j.base.time.getMinuteId()
        #     actor.dbmem.set("mcache_%s"%tt, key, "")
        # elif nrHoursExpiration>0:            
        #     self.set("cache", key, value)
        #     tt=j.base.time.getHourId()
        #     actor.dbmem.set("hcache_%s"%tt, key, "")

    def cacheGet(self,key,deleteAfterGet=False):
        r=self.get("cache",key)
        if deleteAfterGet:
            self.delete("cache", key)
        return r[1]

    def cacheDelete(self,key):
        self.delete("cache", key)

    def cacheExists(self,key):
        return self.exists("cache",key)


    def cacheList(self):

        if "cache" in self.listCategories():
            return self.list("cache")
        else:
            return []

    def cacheExpire(self):
        now=j.base.time.getTimeEpoch()
        for key in self.list():
            expiretime,val=self.get(key)
            if expiretime>now:
                self.delete("cache", key)

    @abstractmethod
    def set(self, category, key, value):
        '''
        Sets a key value pair in the store.

        @param: category of the key value pair
        @type: String

        @param: key of the key value pair
        @type: String
        '''

    @abstractmethod
    def delete(self, category, key):
        '''
        Deletes a key value pair from the store.

        @param: category of the key value pair
        @type: String

        @param: key of the key value pair
        @type: String
        '''

    @abstractmethod
    def exists(self, category, key):
        '''
        Checks if a key value pair exists in the store.

        @param: category of the key value pair
        @type: String

        @param: key of the key value pair
        @type: String

        @return: flag that states if the key value pair exists or not
        @rtype: Boolean
        '''

    @abstractmethod
    def list(self, category, prefix):
        '''
        Lists the keys matching `prefix` in `category`.

        @param category: category the keys should be in
        @type category: String
        @param prefix: prefix the keys should start with
        @type prefix: String
        @return: keys that match `prefix` in `category`.
        @rtype: List(String)
        '''

    @abstractmethod
    def listCategories(self):
        '''
        Lists the categories in this db.

        @return: categories in this db
        @rtype: List(String)
        '''

    @abstractmethod
    def _categoryExists(self, category):
        '''
        Checks if a category exists

        @param category: category to check
        @type category: String
        @return: True if the category exists, False otherwise
        @rtype: Boolean
        '''

    def lock(self,locktype, info="",timeout=5,timeoutwait=0, force=False):
        """
        if locked will wait for time specified
        @param locktype of lock is in style machine.disk.import  (dot notation)
        @param timeout is the time we want our lock to last
        @param timeoutwait wait till lock becomes free
        @param info is info which will be kept in lock, can be handy to e.g. mention why lock taken
        @param force, if force will erase lock when timeout is reached
        @return None
        """
        category="lock"
        lockfree=self._lockWait(locktype, timeoutwait)
        if not lockfree:
            if force==False:
                raise RuntimeError("Cannot lock %s %s"%(locktype, info))
        value = [self.id, j.base.time.getTimeEpoch() + timeout, info]
        encodedValue = json.dumps(value)
        self.settest(category, locktype, encodedValue)

    def lockCheck(self,locktype):
        """
        @param locktype of lock is in style machine.disk.import  (dot notation)
        @return result,id,lockEnd,info  (lockEnd is time when lock times out, info is descr of lock, id is who locked)
                       result is False when free, True when lock is active
        """
        if self.exists("lock",locktype):
            encodedValue = self.get("lock", locktype)
            try:
                id, lockEnd, info = json.loads(encodedValue)
            except ValueError:
                j.logger.exception("Failed to decode lock value")
                raise ValueError("Invalid lock type %s" % locktype)

            if j.base.time.getTimeEpoch() > lockEnd:
                self.delete("lock",locktype)
                return False,0,0,""
            value = [True, id, lockEnd, info]
            return value
        else:
            return False,0,0,""

    def _lockWait(self, locktype,timeoutwait=0):
        """
        wait till lock free
        @return True when free, False when unable to free
        """
        locked,id, lockEnd,info=self.lockCheck(locktype)
        if locked:
            start=j.base.time.getTimeEpoch()
            if lockEnd + timeoutwait < start:
                #the lock was already timed out so is free
                return True

            while True:
                now=j.base.time.getTimeEpoch()
                if now>start+timeoutwait:
                    return False
                if now > lockEnd:
                    return True
                time.sleep(0.1)
        return True

    def unlock(self, locktype,timeoutwait=0, force=False):
        """
        @param locktype of lock is in style machine.disk.import  (dot notation)
        """
        lockfree=self._lockWait(locktype, timeoutwait)
        if not lockfree:
            if force==False:
                raise RuntimeError("Cannot unlock %s" % locktype)
        self.delete("lock",locktype)

    def incrementReset(self, incrementtype, newint=0):
        """
        @param incrementtype : type of increment is in style machine.disk.nrdisk  (dot notation)
        """
        self.set("increment", incrementtype,str(newint))

    def increment(self, incrementtype):
        """
        @param incrementtype : type of increment is in style machine.disk.nrdisk  (dot notation)
        """
        if not self.exists("increment", incrementtype):
            self.set("increment", incrementtype, "1")
            incr=1
        else:
            rawOldIncr = self.get("increment",incrementtype)
            if not rawOldIncr.isdigit():
                raise ValueError("Increment type %s does not have a digit value: %s" % (incrementtype, rawOldIncr))
            oldIncr = int(rawOldIncr)
            incr = oldIncr + 1
            self.set("increment", incrementtype, str(incr))
        return incr

    def getNrRecords(self, incrementtype):
        if not self.exists("increment", incrementtype):
            self.set("increment", incrementtype, "1")
            incr=1
        return int(self.get("increment",incrementtype))

    def settest(self, category, key, value):
        """
        if well stored return True
        """
        self.set(category, key, value)
        if self.get(category, key)==value:
            return True
        return False

    def _assertValidCategory(self, category):
        if not isinstance(category, str) or not category:
            raise ValueError('Invalid category, non empty string expected')

    def _assertValidKey(self, key):
        if not isinstance(key, str) or not key:
            raise ValueError('Invalid key, non empty string expected')

    def _assertExists(self, category, key):
        if not self.exists(category, key):
            errorMessage = 'Key value store doesnt have a value for key '\
                           '"%s" in category "%s"' % (key, category)
            j.logger.log(errorMessage, 4)
            raise KeyError(errorMessage)

    def _assertCategoryExists(self, category):
        if not self._categoryExists(category):
            errorMessage = 'Key value store doesn\'t have a category %s' % (category)
            j.logger.log(errorMessage, 4)
            raise KeyError(errorMessage)

    def now(self):
        """
        return current time (when in appserver will require less time then calling native jumpscale function)
        """
        if j.core.appserver6.runningAppserver<> None:
            return j.core.appserver6.runningAppserver.time
        else:
            return j.base.time.getTimeEpoch()

    def getModifySet(self,category,key,modfunction,**kwargs):
        """
        get value
        give as parameter to modfunction
        try to set by means of testset, if not succesfull try again, will use random function to maximize chance to set
        @param kwargs are other parameters as required (see usage in subscriber function)
        """
        counter=0
        while counter<30:
            data=self.get(category, key)
            data2=modfunction(data)
            if self.settest(category, key, data2):
                break  #go out  of loop, could store well
            time.time.sleep(float(j.base.idgenerator.generateRandomInt(1,10))/50)
            counter+=1
        return data2

    def subscribe(self,subscriberid,category,startid=0):
        """
        each subscriber is identified by a key
        in db there is a dict stored on key for category = category of this method
        value= dict with as keys the subscribers
        {"kristof":[lastaccessedTime,lastId],"pol":...}

        """
        if not self.exists("subscribers",category):
            data={subscriberid:[self.now(),startid]}
        else:
            if startid<>0:
                if not self.exists(category,startid):
                    raise RuntimeError("Cannot find %s:%s in db, cannot subscribe, select valid startid" % (category,startid))

                def modfunction(data,subscriberid,db,startid):
                    data[subscriberid]=[db.now(),startid]
                    return data

                self.getModifySet("subscribers",category,modfunction,subscriberid=subscriberid,db=self,startid=startid)

    def subscriptionGetNextItem(self,subscriberid,category,autoConfirm=True):
        """
        get next item from subscription
        returns
           False,None when no next
           True,the data when a next
        """
        if not self.exists("subscribers",category):
            raise RuntimeError("cannot find subscription")
        data=self.get("subscribers",category)
        if not data.has_key(subscriberid):
            raise RuntimeError("cannot find subscriber")
        lastaccesstime,lastid=data[subscriberid]
        lastid+=1
        if not self.exists(category,startid):
            return False,None
        else:
            return True,self.get(category,startid)
        if autoConfirm:
            self.subscriptionAdvance(subscriberid,category,lastid)
        return self.get(category,key)

    def subscriptionAdvance(self,subscriberid,category,lastProcessedId):

        def modfunction(data,subscriberid,db,lastProcessedId):
            data[subscriberid]=[db.now(),lastProcessedId]
            return data

        self.getModifySet("subscribers",category,modfunction,subscriberid=subscriberid,db=self,lastProcessedId=lastProcessedId)

