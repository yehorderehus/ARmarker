import cv2
import cv2.aruco as aruco
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
import pygame
import numpy as np
from pygame.locals import *
class OpenGLGlyphs:

    def __init__(self):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.cap = cv2.VideoCapture(0)  
        self.marker_size = 0.1 
        self.cap = cv2.VideoCapture(0)

    def _init_gl(self, Width, Height):
        pygame.init()
        display = (Width, Height)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)

    def _draw_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBegin(GL_TRIANGLES)
        glVertex3fv((0, 1, 0))
        glVertex3fv((-1, -1, 0))
        glVertex3fv((1, -1, 0))
        glEnd()

    def _handle_glyphs(self):
        ret, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)

        if ids is not None:
            camera_matrix = np.array([[0, 0, 0],
                                      [0, 0, 0],
                                      [0, 0, 1]])
            dist_coeffs = np.array([0, 0, 0, 0, 0])
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners, self.marker_size, camera_matrix, dist_coeffs)
            for i in range(len(ids)):
                rvec, tvec = rvec[i], tvec[i]
                rotation_matrix, _ = cv2.Rodrigues(rvec)
                transformation_matrix = np.column_stack((rotation_matrix, tvec))
                transformation_matrix = np.vstack((transformation_matrix, [0, 0, 0, 1]))

                glPushMatrix()
                glMultMatrixd(transformation_matrix)

                glBegin(GL_TRIANGLES)
                glVertex3f(-0.5, -0.5, 0)
                glVertex3f(0.5, -0.5, 0)
                glVertex3f(0, 0.5, 0)
                glEnd()

                glPopMatrix()
            

    def main(self):
        self._init_gl(800, 600)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self._handle_glyphs()

            self._draw_scene()
            pygame.display.flip()
            pygame.time.wait(10)

openGLGlyphs = OpenGLGlyphs()
openGLGlyphs.main()