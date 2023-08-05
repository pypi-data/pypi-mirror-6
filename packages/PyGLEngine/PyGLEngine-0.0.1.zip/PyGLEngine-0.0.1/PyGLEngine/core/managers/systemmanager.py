from Queue import Queue
from threading import Thread, Event
from multiprocessing import Process

from DTL.api import apiUtils, BitTracker
from PyGLEngine.core import Base, BaseManager

#------------------------------------------------------------
#------------------------------------------------------------
class System(Base):
    def __init__(self, **kwds):
        super(System, self).__init__(**kwds)
        self.compBits = 0
    
    def addComponent(self, comp_cls):
        #self.compBits |= self.world.ComponentManager.getComponentBit(comp_cls)
        self.compBits |= self.world.EntityManager.getComponentBit(comp_cls)
        
    def addEntity(self, ent):
        if (self.compBits & ent.compBits) == self.compBits:
            self.database[ent.id] = ent
            
    def removeEntity(self, ent):
        try:
            self.database.pop(ent.id)
        except KeyError:
            pass
        
    def process(self, dt):
        [self.processEntity(ent, dt) for ent in self.database.viewvalues()]
        
    def processEntity(self, ent, dt):
        raise NotImplementedError


#------------------------------------------------------------
#------------------------------------------------------------
class ThreadedSystem(Process, System):
    def __init__(self, **kwds):
        self.queue = Queue()
        self._stop = Event()
        Process.__init__(self)
        System.__init__(self, **kwds)
    
    def run(self):
        print '{0} Started!'.format(self.getName())
        while self.isAlive :
            ent, dt = self.queue.get()
            if self._stop.isSet() :
                break
            self.processEntity(ent, dt)
            self.queue.task_done()
            
    def stop(self):
        self._stop.set()
    
    def process(self, dt):
        [self.queue.put((ent, dt)) for ent in self.database.viewvalues()]
        


#------------------------------------------------------------
#------------------------------------------------------------
class SystemBitTracker(BitTracker):
    pass


#------------------------------------------------------------
#------------------------------------------------------------
class SystemManager(BaseManager):
    def __init__(self, **kwds):
        super(SystemManager, self).__init__(**kwds)
        
        self.EntityManager = None
        
    def addSystem(self, system):
        if not issubclass(system, System): raise TypeError
        sys_id = SystemBitTracker.getBit(system)
        self.database[sys_id] = system(world=self.world)
        
    def addEntity(self, ent):
        [system.addEntity(ent) for system in self.systemQueue]
        
    def removeEntity(self, ent):
        [system.removeEntity(ent) for system in self.systemQueue]
        
    def init(self):
        self.EntityManager = self.world.EntityManager
        self.systemQueue = self.getDatabaseByPriority()
        [system.init() for system in self.systemQueue]
            
    def start(self):
        [system.start() for system in self.systemQueue]
            
    def stop(self):
        [system.stop() for system in self.systemQueue]
    
    def update(self, dt):
        #System process parallelization with Threads:
        #First we kick off all the threaded systems so they arn't held up by unthreaded systems
        #Then we kick off all the unthreaded system which will block untill they are done
        #Then we join all of the threaded system's queues so we block untill they are empty
        #After all of this we should be finished processing the systems
        [system.process(dt) for system in self.systemQueue if isinstance(system, ThreadedSystem)]
        #[system.process(dt) for system in self.systemQueue if not isinstance(system, ThreadedSystem)]
        #[system.queue.join() for system in self.systemQueue if isinstance(system, ThreadedSystem)]
