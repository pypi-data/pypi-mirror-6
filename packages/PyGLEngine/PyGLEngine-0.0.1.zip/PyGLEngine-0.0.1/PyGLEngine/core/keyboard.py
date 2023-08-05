from DTL.api import apiUtils
from DTL.qt import QtCore

__all__ = ['Keyboard']

class Keyboard(QtCore.QObject):
    
    def __init__(self, *args, **kwds):
        QtCore.QObject.__init__(self, *args, **kwds)
        apiUtils.synthesize(self, 'keyIsPressed', False)
        apiUtils.synthesize(self, 'mouseIsPressed', False)
        apiUtils.synthesize(self, 'mouseOldX', 0)
        apiUtils.synthesize(self, 'mouseOldY', 0)
        
    def keyPressEvent(self, event):
        print event.key()

    def timerEvent(self, event):
        print event.timerId()
    
    def mouseMoveEvent(self, mouseEvent):
        if int(mouseEvent.buttons()) != QtCore.Qt.NoButton :# user is dragging
            delta_x = mouseEvent.x() - self._mouseOldX
            delta_y = self._mouseOldY - mouseEvent.y()
            
            
            print "Mouse Move ", delta_x, delta_y
            '''
            if int(mouseEvent.buttons()) & QtCore.Qt.LeftButton :
                self.camera.orbit(self.oldx,self.oldy,mouseEvent.x(),mouseEvent.y())
            elif int(mouseEvent.buttons()) & QtCore.Qt.RightButton :
                self.camera.dollyCameraForward( 3*(delta_x+delta_y), False )  
            elif int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
                self.camera.translateSceneRightAndUp( delta_x, delta_y )
            else:
                return
            self.update()
            '''
        self._mouseOldX = mouseEvent.x()
        self._mouseOldY = mouseEvent.y()
        
    def wheelEvent(self, event):
        print "Wheel ", event.delta()
        #self.camera.dollyCameraForward( event.delta(), False )
        #self.update()

    def mouseDoubleClickEvent(self, mouseEvent):
        print "double click"

    def mousePressEvent(self, e):
        print "mouse press"
        self._mouseIsPressed = True

    def mouseReleaseEvent(self, e):
        print "mouse release"
        self._mouseIsPressed = False
