from PyGLEngine.core import ComponentTypeManager

#------------------------------------------------------------
#------------------------------------------------------------
class EntitySystem(object):
    
    def __init__(self, *components):
        self.world = None
        self.systemBit = 0
        self.typeFlags = 0
        
        self.actives = {}
        self.enabled = True

        for comp in components:
            self.addComponentType(comp)
            
    def addComponentType(self, comp):
        self.typeFlags |= ComponentTypeManager.getBit(comp)
            
    def toggle(self):
        self.enabled = not self.enabled

    def change(self, ent_id):
        ent = self.world.EntityManager.getEntity(ent_id)
        contains = (self.systemBit & ent.getSystemBits()) == self.systemBit
        interest = (self.typeFlags & ent.getTypeBits()) == self.typeFlags

        if interest and not contains and self.typeFlags > 0:
            self.actives[ent_id] = ent
            ent.addSystemBit(self.systemBit)
            self.added(ent_id)
        elif not interest and contains and self.typeFlags > 0:
            self.remove(ent_id)
        
    def remove(self, ent_id):
        ent = self.world.EntityManager.getEntity(ent_id)
        self.actives.pop(ent_id)
        ent.removeSystemBit(self.systemBit)
        self.removed(ent_id)

    def process(self):
        if self.canProcess():
            self.begin()
            self.processEntities()
            self.end()

    
    ##Virtual Methods
    def initialize(self):
        pass
    def added(self, ent_id):
        pass
    def removed(self, ent_id):
        pass
    def canProcess(self):
        return self.enabled
    def begin(self):
        pass
    def processEntities(self):
        raise NotImplementedError  
    def end(self):
        pass
    ##
