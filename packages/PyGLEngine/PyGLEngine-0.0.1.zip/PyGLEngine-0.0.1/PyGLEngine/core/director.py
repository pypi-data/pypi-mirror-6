from DTL.api import apiUtils
from pyglet import app, event, clock

__all__ = ['director']

class Director(event.EventDispatcher):
    def init(self, *args, **kwargs):
        apiUtils.synthesize(self, 'sceneStack', [])
        apiUtils.synthesize(self, 'activeScene', None)
        apiUtils.synthesize(self, 'nextScene', None)
        apiUtils.synthesize(self, 'eventLoop', app.EventLoop())
        apiUtils.synthesize(self, 'clock', clock.Clock())
        self.event = self._eventLoop.event

    def run(self, scene):
        """Runs a scene, entering in the Director's main loop.

        :Parameters:
            `scene` : `Scene`
                The scene that will be run.
        """
        self._set_scene( scene )
        self._eventLoop.run()


    def push(self, scene):
        """Suspends the execution of the running scene, pushing it
        on the stack of suspended scenes. The new scene will be executed.

        :Parameters:
            `scene` : `Scene`
                It is the scene that will be run.
           """
        self.dispatch_event("on_push", scene )

    def on_push( self, scene ):
        self._nextScene = scene
        self._sceneStack.append( self._activeScene )

    def pop(self):
        """If the scene stack is empty the appication is terminated.
            Else pops out a scene from the stack and sets as the running one.
        """
        self.dispatch_event("on_pop")

    def on_pop(self):
        if len(self._sceneStack) == 0:
            pass #TODO: kill app  self.terminate_app = True
        else:
            self._nextScene = self._sceneStack.pop()

    def replace(self, scene):
        """Replaces the running scene with a new one. The running scene is terminated.

        :Parameters:
            `scene` : `Scene`
                It is the scene that will be run.
        """
        self._nextScene = scene

    def _set_scene(self, scene ):
        """Makes scene the current scene

            Operates on behalf of the public scene switching methods
            User code must not call directly
        """
        self._nextScene = None

        # always true except for first scene in the app
        if self._activeScene is not None:
            self._activeScene.disable()

        old = self._activeScene
        self._activeScene = scene

        # always true except when terminating the app
        if self._activeScene is not None:
            self._activeScene.enable()

        return old
    
    def scheduleInterval(self, callback, interval, *args, **kwargs):
        """
        Schedule a function to be called every `interval` seconds.

        Specifying an interval of 0 prevents the function from being
        called again (see `schedule` to call a function as often as possible).

        The callback function prototype is the same as for `schedule`.

        :Parameters:
            `callback` : function
                The function to call when the timer lapses.
            `interval` : float
                The number of seconds to wait between each call.
        """
        self._clock.schedule_interval(callback, interval, *args, **kwargs)

    def schedule(self, callback, *args, **kwargs):
        """
        Schedule a function to be called every frame.

        The function should have a prototype that includes ``dt`` as the
        first argument, which gives the elapsed time, in seconds, since the
        last clock tick.  Any additional arguments given to this function
        are passed on to the callback::

            def callback(dt, *args, **kwargs):
                pass

        :Parameters:
            `callback` : function
                The function to call each frame.
        """
        self._clock.schedule(callback, *args, **kwargs)

    def unschedule(self, callback):
        """
        Remove a function from the schedule.

        If the function appears in the schedule more than once, all occurances
        are removed.  If the function was not scheduled, no error is raised.

        :Parameters:
            `callback` : function
                The function to remove from the schedule.
        """
        self._clock.unschedule( callback )



director = Director()

Director.register_event_type('on_push')
Director.register_event_type('on_pop')

director.init()
