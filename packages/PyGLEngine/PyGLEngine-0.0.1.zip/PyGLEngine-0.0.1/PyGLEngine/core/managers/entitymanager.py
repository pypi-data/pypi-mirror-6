from DTL.api import apiUtils, BitTracker
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
class Entity(Base):
    def __init__(self):
        super(Entity, self).__init__()
        self.init()
        
    def addComponent(self, comp_cls):
        self.database[apiUtils.getClassName(comp_cls)] = comp_cls

#------------------------------------------------------------
#------------------------------------------------------------
class EntityProxy(Base):
    def __init__(self, world=None):
        super(EntityProxy, self).__init__(world=world)
        self.id = 0
        self.oldCls = None
        self.compBits = 0
        
        #we cache these off to make accessing these speedier
        self.ComponentManager = world.ComponentManager
        self.GroupManager = world.GroupManager
        self.TagManager = world.TagManager
        
    def reset(self):
        #self.ComponentManager.removeAllComponents(self.id)
        self.database = {}
        self.compBits = 0
    
    def __str__(self):
        return "{0}".format(self.__repr__())
    
    def __repr__(self):
        return "<EntityProxy '{0}' | id {1}>".format(self.oldCls, self.id)
    
    def __getattr__(self, name):
        try:
            return self.database[name]
        except:
            raise AttributeError
    
    def addComponent(self, comp_cls):
        #comp_id = self.ComponentManager.addComponent(self.id, comp_cls)
        if not issubclass(comp_cls, Component): raise TypeError
        comp_id = ComponentBitTracker.getBit(comp_cls)
        self.database[apiUtils.getClassName(comp_cls).lower()] = comp_cls(world=self.world)        
        self.compBits |= comp_id
    
    def removeComponent(self, comp_id):
        if bin(comp_id).count("1") != 1 : raise ValueError('{} is not a single bit'.format(comp_id))
        #self.ComponentManager.removeComponent(self.id, comp_id)
        self.database.pop(comp_id)
        self.compBits &= ~comp_id

    def getComponent(self, comp_id):
        #return self.ComponentManager.getComponent(self.id, comp_id)
        return self.database[comp_id]
    
    def getComponents(self):
        #return self.ComponentManager.getComponents(self.id)
        return self.database.viewvalues()

    def setGroup(self, group_name):
        self.GroupManager.addEntityToGroup(group, self.id)
        
    def setTag(self, tag):
        self.TagManager.addTag(tag, self.id)
        
    def getTag(self):
        return self.TagManager.getTagsByValue(self.id)
    
    def init(self):
        self.world.SystemManager.addEntity(self)


#------------------------------------------------------------
#------------------------------------------------------------
class EntityBitTracker(BitTracker):
    pass

#------------------------------------------------------------
#------------------------------------------------------------
class EntityManager(BaseManager):
    REMOVED_COMPONENT_EVENT = "RemovedComponent"
    REMOVED_ENTITY_EVENT    = "RemovedEntity"
    ADDED_COMPONENT_EVENT   = "AddedComponent"
    ADDED_ENTITY_EVENT      = "AddedEntity"

    def __init__(self, **kwds):
        super(EntityManager, self).__init__(**kwds)
        
        #List of the avaible entities, so we can reuse them
        self.entityCache = list()
        #This is the nextId to append to the Entity class name if we need to create a new entity
        #Otherwise we just reuse them
        self.nextId = 0
        #This is the bit mask for all the active entities
        self.entityMask = 0
        #We don't deactive an entity untill the next update frame
        self.deactivateQueue = set()
                
    def scheduleDeactivate(self, ent_id):
        self.deactivateQueue.add(ent_id)
    
    def update(self, dt):
        [self.deactivateEntity(ent_id) for ent_id in self.deactivateQueue]
        self.deactivateQueue = set()
            
    def getEntity(self, ent_id):
        return self.database[ent_id]

    def addEntity(self, ent_proxy):
        if not issubclass(ent_proxy, Entity): raise TypeError
        ent_proxy = ent_proxy()
        try:
            ent = self.entityCache.pop()
        except IndexError:
            ent = EntityProxy(world=self.world)
            ent_name = apiUtils.getClassName(EntityProxy) + str(self.nextId)
            ent.id = EntityBitTracker.getBit(ent_name)
            self.nextId += 1
        
        ent.oldCls = apiUtils.getClassName(ent_proxy)
        [ent.addComponent(comp_cls) for comp_cls in ent_proxy.database.viewvalues()]
        self.entityMask += ent.id
        self.database[ent.id] = ent
        return ent.id
    
    def deactivateEntity(self, ent_id):
        try:
            ent = self.database.pop(ent_id)
        except KeyError:
            return
        
        self.entityMask -= ent.id
        ent.reset()
        self.entityCache.append(ent)

    def removeEntity(self, ent_id):
        self.deactivateQueue.update(ent_id)
        
    def removeAllEntities(self):
        self.deactivateQueue.update(self.database.keys())
        
    def getActiveEntities(self):
        return self.database.viewvalues()
    
    def getComponentBit(self, comp_cls):
        return ComponentBitTracker.getBit(comp_cls)
    
    def init(self):
        [ent.init() for ent in self.database.viewvalues()]
