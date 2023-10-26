import cv2
import numpy as np
import cv2.aruco as aruco
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def draw_cube():
    glBegin(GL_QUADS)

    glVertex3f(-1, -1, -1)
    glVertex3f( 1, -1, -1)
    glVertex3f( 1,  1, -1)
    glVertex3f(-1,  1, -1)

    glVertex3f(-1, -1, 1)
    glVertex3f( 1, -1, 1)
    glVertex3f( 1,  1, 1)
    glVertex3f(-1,  1, 1)

    glVertex3f(-1, -1, -1)
    glVertex3f(-1,  1, -1)
    glVertex3f(-1,  1,  1)
    glVertex3f(-1, -1,  1)

    glVertex3f(1, -1, -1)
    glVertex3f(1,  1, -1)
    glVertex3f(1,  1,  1)
    glVertex3f(1, -1,  1)

    glVertex3f(-1, 1, -1)
    glVertex3f( 1, 1, -1)
    glVertex3f( 1, 1,  1)
    glVertex3f(-1, 1,  1)

    glVertex3f(-1, -1, -1)
    glVertex3f( 1, -1, -1)
    glVertex3f( 1, -1,  1)
    glVertex3f(-1, -1,  1)

    glEnd()

def process_frame(frame, aruco_dict):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    parameters = aruco.DetectorParameters()
    corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        center = corners[0][0].mean(axis=0)

        if center is not None:
            glPushMatrix()
            glTranslatef(center[0], center[1], 0)
            draw_cube()
            glPopMatrix()

    cv2.imshow("Marker", frame)

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error(camera)")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        process_frame(frame, aruco_dict)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    main()
