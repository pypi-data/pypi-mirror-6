import sys
import math
from DTL.qt import QtCore, QtGui
from DTL.qt.QtOpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from DTL.math import Vec3, Point3D, Matrix44

from PyGLEngine.core import Camera

__all__ = ['Viewport']

class Viewport(QGLWidget):

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.camera = Camera()
        self.camera.setSceneRadius( 2 )
        self.camera.reset()

    def paintGL(self):
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        self.camera.transform()
        glMatrixMode( GL_MODELVIEW );
        glLoadIdentity();

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glDepthFunc( GL_LEQUAL );
        glEnable( GL_DEPTH_TEST );
        glEnable( GL_CULL_FACE );
        glFrontFace( GL_CCW );
        glDisable( GL_LIGHTING );
        glShadeModel( GL_FLAT );

        glColor(1.0, 1.0, 1.0)
        glBegin(GL_LINE_STRIP)
        glVertex(-1,-1,-1)
        glVertex( 1,-1,-1)
        glVertex( 1, 1,-1)
        glVertex(-1, 1,-1)
        glVertex(-1,-1, 1)
        glVertex( 1,-1, 1)
        glVertex( 1, 1, 1)
        glVertex(-1, 1, 1)
        glEnd()
        glColor(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex( 1, 0, 0)
        glEnd()
        glColor(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex( 0, 1, 0)
        glEnd()
        glColor(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex( 0, 0, 1)
        glEnd()

        glFlush()

    def resizeGL(self, widthInPixels, heightInPixels):
        self.camera.setViewportDimensions(widthInPixels, heightInPixels)
        glViewport(0, 0, widthInPixels, heightInPixels)

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)


