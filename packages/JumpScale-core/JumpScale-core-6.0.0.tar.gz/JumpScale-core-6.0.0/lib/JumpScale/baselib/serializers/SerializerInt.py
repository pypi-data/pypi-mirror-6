

class SerializerInt(object):
    def dumps(self,obj):
        return str(obj)
    def loads(self,s):
        return int(s)