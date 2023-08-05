from PyGLEngine.core import BaseManager

#------------------------------------------------------------
#------------------------------------------------------------
class GroupManager(BaseManager):
    def __init__(self, **kwds):
        super(GroupManager, self).__init__(**kwds)
        
    def formatGroupName(self, group_name):
        return group_name.lower()
    
    def addEntityToGroup(self, group_name, ent_id):
        group_name = self.formatGroupName(group_name)
        try:
            self.database[group_name] += ent_id
        except KeyError:
            self.database[group_name] = ent_id
    
    def removeEntityFromGroup(self, group_name, ent_id):
        group_name = self.formatGroupName(group_name)
        for key in [g for g in self.getGroups(ent_id) if g == group_name]:
            self.database[key] -= ent_id()
        
    def removeEntity(self, ent_id):
        for group_name in [g for g in self.getGroups(ent_id)]:
            self.database[group_name] -= ent_id
        
    def getGroups(self, ent_id):
        found_groups = []
        for group_name, entity_mask in self.database.viewitems() :
            bit_index = ent_id.bit_length() - 1
            if (entity_mask & (1<<bit_index)):
                found_groups.append(group_name)
        return found_groups
    
    def getEntities(self, group_name):
        return self.database.get(group_name.lower(),0)        
    
    def isGrouped(self, ent_id):
        return self.getGroups(ent_id) == []