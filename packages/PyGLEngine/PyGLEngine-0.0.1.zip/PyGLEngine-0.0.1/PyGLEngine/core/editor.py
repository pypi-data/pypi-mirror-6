from DTL.qt import QtCore, QtGui
from PyGLEngine.core import GameClient

__all__ = ['Editor']

class Editor(GameClient):
    
    def __init__(self, *args, **kwds):
        GameClient.__init__(self, *args, **kwds)
        
    def show(self):
        #This double show with resize and center keeps the windows maximize and fullscreen stuff working in a coherient manner when started up
        super(Editor, self).show()
        self.resize(800,600)
        self.center()
        super(Editor, self).showMaximized()

    def save(self):
        pass

    def undo(self):
        pass
    
    def redo(self):
        pass

    def about(self):
        QtGui.QMessageBox.about(self, "About", "")

    def createActionsData(self):
        current_actions = super(Editor, self).createActionsData()
        current_actions.update({'&Save':{'icon':QtGui.QIcon(':/images/save.png'),
                                         'shortcut':QtGui.QKeySequence.Save,
                                         'statusTip':'Save',
                                         'triggered':self.save},
                                '&Undo':{'icon':QtGui.QIcon(':/images/back.png'),
                                         'shortcut':QtGui.QKeySequence.Undo,
                                         'statusTip':'Undo',
                                         'triggered':self.undo},
                                '&Redo':{'icon':QtGui.QIcon(':/images/forward.png'),
                                         'shortcut':QtGui.QKeySequence.Redo,
                                         'statusTip':'Redo',
                                         'triggered':self.redo}})
        
        return current_actions
    
    def createMenusData(self):
        return [('&File',[self.action_save, '|', self.action_quit]),
                ('&Edit',[self.action_undo, self.action_redo]),
                ('&View',[self.action_toggle_fullscreen]),
                ('|',[]),
                ('&Help',[self.action_about])]
                        
    def createToolBarsData(self):
        return [('File',[self.action_save, '|', self.action_quit]),
                ('Edit',[self.action_undo, self.action_redo])]
    
    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
        
    def createDocks(self):
        self.customerList = QtGui.QListWidget()
        self.customerList.addItems((
            "John Doe, Harmony Enterprises, 12 Lakeside, Ambleton",
            "Jane Doe, Memorabilia, 23 Watersedge, Beaton",
            "Tammy Shea, Tiblanka, 38 Sea Views, Carlton",
            "Tim Sheen, Caraba Gifts, 48 Ocean Way, Deal",
            "Sol Harvey, Chicos Coffee, 53 New Springs, Eccleston",
            "Sally Hobart, Tiroli Tea, 67 Long River, Fedula"))
        
        self.paragraphsList = QtGui.QListWidget()
        self.paragraphsList.addItems((
            "Thank you for your payment which we have received today.",
            "Your order has been dispatched and should be with you within "
                "28 days.",
            "We have dispatched those items that were in stock. The rest of "
                "your order will be dispatched once all the remaining items "
                "have arrived at our warehouse. No additional shipping "
                "charges will be made.",
            "You made a small overpayment (less than $5) which we will keep "
                "on account for you, or return at your request.",
            "You made a small underpayment (less than $1), but we have sent "
                "your order anyway. We'll add this underpayment to your next "
                "bill.",
            "Unfortunately you did not send enough money. Please remit an "
                "additional $. Your order will be dispatched as soon as the "
                "complete amount has been received.",
            "You made an overpayment (more than $5). Do you wish to buy more "
                "items, or should we return the excess to you?"))
    
    def createDockWindowsData(self):
        return [('Customers',{'allowed_areas':QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea,
                             'default_area':QtCore.Qt.RightDockWidgetArea,
                             'widget':self.customerList}),
                ('Paragraphs',{'allowed_areas':QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea,
                              'default_area':QtCore.Qt.RightDockWidgetArea,
                              'widget':self.paragraphsList})]
            
    def createOtherUI(self):
        pass

if __name__ == '__main__':
    Editor.run()
