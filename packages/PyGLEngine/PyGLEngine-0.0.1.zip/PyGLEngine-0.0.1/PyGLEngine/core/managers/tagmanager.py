from PyGLEngine.core import BaseManager

#------------------------------------------------------------
#------------------------------------------------------------
class TagManager(BaseManager):
    def __init__(self, **kwds):
        super(TagManager, self).__init__(**kwds)

    def addTag(self, tag, value):
        self.database[tag] = value
    
    def getValueByTag(self, tag):
        return self.database.get(tag)
    
    def getTagsByValue(self, value):
        try:
            return [k for k, v in self.database.viewitems() if v == value]
        except :
            return ''
