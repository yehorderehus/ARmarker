# OpenGL imports
from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
from OpenGL.GL.shaders import compileProgram, compileShader

# Other imports
import pyrr
import os
import glfw # maybe will be changed

# Common imports
from main_objtexloader import load_texture
from main_objloader import ObjLoader

# Read shader files
def read_shader_file(file_name):
    file_path = os.path.join('shaders_src', file_name)
    with open(file_path, 'r') as file:
        return file.read()

vertex_src = read_shader_file('vertex_src.txt')
fragment_src = read_shader_file('fragment_src.txt')

# GLFW callback functions
def window_resize(window, width, height):
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

# Initializing GLFW library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# Creating the window
window = glfw.create_window(1280, 720, "My OpenGL window", None, None)

# Check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# Set window's position
glfw.set_window_pos(window, 400, 200)

# Set the callback function for window resize
glfw.set_window_size_callback(window, window_resize)

# Make the context current
glfw.make_context_current(window)

# Load the model
model_indices, model_buffer = ObjLoader.load_model("objects/chibi.obj")

# Load the model textures
textures = glGenTextures(2)
load_texture("objects/chibi.png", textures[0])

# Compile the shader
shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

# Create and bind a VAO and VBO for the model
VAO = glGenVertexArrays(2)
VBO = glGenBuffers(2)

# Model VAO
glBindVertexArray(VAO[0])

# Model VBO
glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
glBufferData(GL_ARRAY_BUFFER, model_buffer.nbytes, model_buffer, GL_STATIC_DRAW)

# Model vertices
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(0))

# Model textures
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(12))

# Model normals
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(20))
glEnableVertexAttribArray(2)

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 100)
model_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, -5, -10]))

# eye, target, up
view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 0, 8]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

# The preview application loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())
    model = pyrr.matrix44.multiply(rot_y, model_pos)

    # Draw the model
    glBindVertexArray(VAO[0])
    glBindTexture(GL_TEXTURE_2D, textures[0])  
    glDrawArrays(GL_TRIANGLES, 0, len(model_indices))
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

    # Swap front and back buffers
    glfw.swap_buffers(window)

# Terminate GLFW, free up allocated resources
glfw.terminate()

class OpenGL:
    def __init__(self):
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()     

    def init(self):
        pass

class Object:
    def __init__(self):
        pass

    def load(self):
        pass

class Preview:
    def __init__(self):
        pass

    def run(self):
        pass


if __name__ == "__main__":
    OpenGL().init()
    Object().load()
    Preview().run() # the idea is that preview will be able to be toggled on and off; for now we have to dig into opengl and divide preview / model init