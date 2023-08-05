from copy import deepcopy
from DTL.api import apiUtils
from PyGLEngine.core import director


#TODO:  what we should have is these seperate components:
#Node - for hierachcial stuff
#Scheduler - for scheduling functions
#Handler - for adding event handlers
#This way you can have an object that is just a scheduler and handler without the parent child stuff

class Node(object):
    _is_event_handler = False
    
    def __init__(self, name='', parent=None):
        apiUtils.synthesize(self, 'name', name)
        apiUtils.synthesize(self, 'parent', parent)
        apiUtils.synthesize(self, 'children', [])
        apiUtils.synthesize(self, 'scheduled', False)
        apiUtils.synthesize(self, 'scheduledCalls', [])
        apiUtils.synthesize(self, 'scheduledIntervalCalls', [])
        apiUtils.synthesize(self, 'isRunning', False)      
        apiUtils.synthesize(self, 'handlersEnabled', False)
        if parent != None :
            parent._children.append(self)
            
    def __repr__(self):
        return 'Node({0})'.format(self._name)
    
    def __iter__(self):
        return self._children
        
    def copy(self):
        return deepcopy(self)
    
    def childCount(self):
        return len(self._children)
    
    def setParent(self, new_parent):
        if new_parent != None and self._parent != None :
            index = self._parent._children.index(self)
            if self._parent.removeChild(index) == False :
                raise Exception('Unable to remove {0} from {1} children'.format(self, self._parent))
            new_parent._children.append(self)
        self._parent = new_parent
            
    def addChild(self, child):
        self._children.append(child)
        child.setParent(self)
        return True
        
    def insertChild(self, index, child):
        if index < 0 or index > len(self._children):
            return False
        
        self._children.insert(index, child)
        child.setParent(self)
        return True
    
    def removeChild(self, index):
        if index < 0 or index > len(self._children):
            return False
        
        child = self._children.pop(index)
        child.setParent(None)

        return True
    
    def child(self, index):
        return self._children[index]
    
    def index(self):
        if self.parent is None:
            return None
        return self._parent._children.index(self)
    
    def walk(self, callback, collect=None):
        """
        Executes callback on all the subtree starting at self.
        returns a list of all return values that are not none
        """
        if collect is None:
            collect = []

        r = callback(self)
        if r is not None:
            collect.append( r )

        for c in self:
            c.walk(callback, collect)

        return collect
    
    def enable(self):
        #Top Down Enable
        self.resumeScheduler()
        self.pushAllHandlers()
        self._isRunning = True
        self._handlersEnabled = True        
        for c in self:
            c.enable()        
        
    def disable(self):
        #Bottom Up Disable
        for c in self:
            c.disable()         

        self.pauseScheduler()
        self.removeAllHandlers()
        self._isRunning = False
        self._handlersEnabled = False        
    
    
    def pushAllHandlers(self):
        """ registers itself to receive director events and propagates
            the call to childs.
            class member is_event_handler must be True for this to work"""
        if self._is_event_handler:
            director.push_handlers( self )

    def removeAllHandlers(self):
        """ de-registers itself to receive director events and propagates
            the call to childs.
            class member is_event_handler must be True for this to work"""
        if self._is_event_handler:
            director.remove_handlers( self )
            
    def enableHandlers(self, value=True):
        if value and not self._handlersEnabled and self._isRunning:
            self.pushAllHandlers()
        elif not value and self._handlersEnabled and self._isRunning:
            self.removeAllHandlers()
        self._handlersEnabled = value
        
    def resumeScheduler(self):
        """
        Time will continue/start passing for this node and callbacks
        will be called, worker actions will be called
        """
        for c, i, a, k in self._scheduledIntervalCalls:
            director.scheduleInterval(c, i, *a, **k)
        for c, a, k in self._scheduledCalls:
            director.schedule(c, *a, **k)

    def pauseScheduler(self):
        """
        Time will stop passing for this node: scheduled callbacks will
        not be called, worker actions will not be called
        """
        for args in self._scheduledIntervalCalls:
            director.unschedule(args[0])
        for args in self._scheduledCalls:
            director.unschedule(args[0])
            
    def enableScheduler(self, value=True):
        if value and not self._isRunning:
            self.resumeScheduler()
        elif not value and self._isRunning:
            self.pauseScheduler()
        self._isRunning = value
    
    def scheduleInterval(self, callback, interval, *args, **kwargs):
        """See director.scheduleInterval"""
        if self._isRunning:
            director.scheduleInterval(callback, interval, *args, **kwargs)
        self._scheduledIntervalCalls.append(
                (callback, interval, args, kwargs)
                )

    def schedule(self, callback, *args, **kwargs):
        """See director.schedule"""
        if self.is_running:
            director.schedule(callback, *args, **kwargs)
        self._scheduledCalls.append(
                (callback, args, kwargs)
                )

    def unschedule(self, callback):
        """See director.unschedule"""

        total_len = len(self._scheduledCalls + self._scheduledIntervalCalls)
        self._scheduledCalls = [
                c for c in self._scheduledCalls if c[0] != callback
                ]
        self._scheduledIntervalCalls = [
                c for c in self._scheduledIntervalCalls if c[0] != callback
                ]

        if self._isRunning:
            director.unschedule( callback )

    