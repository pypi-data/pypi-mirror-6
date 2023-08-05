import time

from DTL.api import apiUtils
from PyGLEngine.core import BaseManager, SystemManager, EntityManager, TagManager, GroupManager

__all__ = ['World']

#------------------------------------------------------------
#------------------------------------------------------------
class World(BaseManager):
    '''The main class the represents the game world simulation, or manager of managers'''
    #------------------------------------------------------------
    def __init__(self):
        super(World, self).__init__()
        self.Delta = 0 
        self.managerQueue = list()
        
        #This should get moved a configuration somehow
        self.addManager(TagManager, priority=-4)
        self.addManager(GroupManager, priority=-3)
        self.addManager(SystemManager, priority=-2)
        self.addManager(EntityManager, priority=-1)
        
    def addManager(self, manager, priority=0):
        if not issubclass(manager, BaseManager): raise TypeError(manager)
        manager_name = apiUtils.getClassName(manager)
        if manager_name not in self.database.viewkeys():
            manager_cls = manager(priority=priority, world=self)
            self.database[manager_name] = manager_cls
    
    def addSystem(self, system):
        self.SystemManager.addSystem(system)
        
    def addEntity(self, entity):
        self.EntityManager.addEntity(entity)
    
    def init(self):
        #We setup the priority queue just on init
        self.managerQueue = self.getDatabaseByPriority()
        [manager.init() for manager in self.managerQueue]
        #We want to make sure all the managers are init'd before we start them
        self.start()
    
    def start(self):
        [manager.start() for manager in self.managerQueue]
    
    def stop(self):
        [manager.stop() for manager in self.managerQueue]
    
    def update(self, dt):
        [manager.update(dt) for manager in self.managerQueue]
