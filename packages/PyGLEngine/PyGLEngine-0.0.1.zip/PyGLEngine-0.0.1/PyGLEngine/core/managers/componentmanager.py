from DTL.api import BitTracker
from PyGLEngine.core import Base, BaseManager

#------------------------------------------------------------
#------------------------------------------------------------
class Component(Base):
    def __init__(self, **kwds):
        super(Component, self).__init__(**kwds)
        self.init()


#------------------------------------------------------------
#------------------------------------------------------------
class ComponentBitTracker(BitTracker):
    pass


#------------------------------------------------------------
#------------------------------------------------------------
class ComponentManager(BaseManager):
    '''This class manages all the components registered'''
    def __init__(self, **kwds):
        super(ComponentManager, self).__init__(**kwds)
        self.deactivateQueue = set()
        
    def scheduleDeactivate(self, ent_id):
        self.deactivateQueue.add(ent_id)
    
    def update(self, dt):
        for id_tuple in self.deactivateQueue :
            self.deactivateComponent(id_tuple)
        self.deactivateQueue = set()
        
    def addComponent(self, ent_id, comp_cls):
        if not issubclass(comp_cls, Component): raise TypeError
        comp_id = ComponentBitTracker.getBit(comp_cls)
        try :
            ent_comps = self.database[ent_id]
        except KeyError:
            ent_comps = dict()
            self.database[ent_id] = ent_comps
        
        ent_comps[comp_id] = comp_cls(world=self.world)
        return comp_id
    
    def deactivateComponet(self, id_tuple):
        try:
            ent = self.database[id_tuple[0]].pop(id_tuple[1])
        except KeyError:
            return
    
    def removeComponent(self, ent_id, comp_id):
        self.deactivateQueue.add((ent_id, comp_id))
        
    def removeAllComponents(self, ent_id):
        self.deactivateQueue.update(self.database.pop(ent_id).items())
        
    def getComponentBit(self, comp_cls):
        return ComponentBitTracker.getBit(comp_cls)
        
    def getComponent(self, ent_id, comp_id):
        return self.database.get(ent_id,{}).get(comp_id)
    
    def getComponents(self, ent_id):
        return self.database.get(ent_id,[])
        

