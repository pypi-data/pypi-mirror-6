from DTL.gui import MainWindow
from PyGLEngine.core import World, Viewport

__all__ = ['GameClient']

class GameClient(MainWindow):
    def __init__(self, *args, **kwds):
        MainWindow.__init__(self, *args, **kwds)
        
    def onInit(self):
        self.toggleFullscreen()
        self.menuBar().setVisible(False)
    
    def createCentralWidget(self):
        return Viewport(self)
        
    def eventFilter(self, obj, event):
        print obj, event

if __name__ == '__main__':
    GameClient.run()
