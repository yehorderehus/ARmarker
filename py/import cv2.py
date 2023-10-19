import cv2
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
import pygame
import numpy as np
from pygame.locals import *
import threading

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters()

INVERSE_MATRIX = np.array([[1.0, 1.0, 1.0, 1.0],
                           [-1.0, -1.0, -1.0, -1.0],
                           [-1.0, -1.0, -1.0, -1.0],
                           [1.0, 1.0, 1.0, 1.0]])

def draw_3d_object():
    glBegin(GL_TRIANGLES)
    glVertex3f(-1, -1, -1)
    glVertex3f(1, -1, -1)
    glVertex3f(0, 1, -1)
    glEnd()

def _init_gl(Width, Height):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(37, 1.3, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 300, 200, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)

def process_video(video_cap):
    video_ret, video_shot = video_cap.read()

    if not video_ret:
        video_cap.release()
        cv2.destroyAllWindows()
        raise ValueError("Unable to read frame from video capture device")
    rotation_vector = np.array([0.0, 0.0, 0.0])
    markerCorners_video, markerIds_video, rejectedMarkers_video = cv2.aruco.detectMarkers(video_shot, aruco_dict, parameters=parameters)
    if markerIds_video is not None:
        for i in range(len(markerIds_video)):
            translation_vector = markerCorners_video[i][0].mean(axis=0)
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

            glPushMatrix()
            glTranslatef(*translation_vector)
            glMultMatrixd(rotation_matrix.T)
            draw_3d_object()
            _init_gl(window_width, window_height)
            glPopMatrix()

pygame.init()
window_width = 1080
window_height = 720

screen = pygame.display.set_mode((window_width, window_height))

video_cap = cv2.VideoCapture(0)

running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    ret, frame = video_cap.read()
    if not ret:
        break

    process_video(video_cap)
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (window_width, window_height))

    screen.blit(frame, (0, 0))
    pygame.display.update()

pygame.quit()
video_cap.release()
cv2.destroyAllWindows()
