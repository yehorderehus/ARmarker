# OpenGL imports
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

# Other imports
import os
import glfw
import pyrr
import numpy as np
from PIL import Image

# Common imports
from model_loader import ModelLoader


class ShaderLoader:
    @staticmethod
    def read_shader_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    @staticmethod
    def load_shader_program(vertex_src_path, fragment_src_path):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        vertex_src_path = os.path.join(script_dir, vertex_src_path)
        fragment_src_path = os.path.join(script_dir, fragment_src_path)

        vertex_src = ShaderLoader.read_shader_file(vertex_src_path)
        fragment_src = ShaderLoader.read_shader_file(fragment_src_path)

        return compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )


class ModelSetUp:
    def __init__(self, file=None, texture_file=None) -> None:
        # Set initial parameters
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.textures = glGenTextures(1)
        self.model_indices = None
        self.model_buffer = None

        # Set model itself
        if file:
            self.model_loader(file)
            self.model_parameters()
        if texture_file:
            self.texture_loader(texture_file, self.textures)

    def model_loader(self, path):
        self.model_indices, self.model_buffer = ModelLoader.load_model(path)

    def texture_loader(self, path, texture):
        # Bind texture
        glBindTexture(GL_TEXTURE_2D, texture)

        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Load image
        image = Image.open(path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image_data = image.convert("RGBA").tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    def model_parameters(self):
        # Model VAO
        glBindVertexArray(self.VAO)

        # Model VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.model_buffer.nbytes,
                     self.model_buffer, GL_STATIC_DRAW)

        # Model vertices
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 3, GL_FLOAT, GL_FALSE,
            self.model_buffer.itemsize * 8, ctypes.c_void_p(0)
        )

        # Model textures
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1, 2, GL_FLOAT, GL_FALSE,
            self.model_buffer.itemsize * 8, ctypes.c_void_p(12)
        )

        # Model normals
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(
            2, 3, GL_FLOAT, GL_FALSE,
            self.model_buffer.itemsize * 8, ctypes.c_void_p(20)
        )


# TODO Functions separation and optimization
class OpenGLContext:
    def __init__(self, pov, near, far, window_width, window_height) -> None:
        self.pov, self.near, self.far = pov, near, far

        self.model_setup = None

        if not glfw.init():
            raise Exception("glfw can not be initialized!")

        # Set window
        glfw.window_hint(glfw.VISIBLE, glfw.TRUE)
        self.window = glfw.create_window(window_width, window_height,
                                         "OpenGL Context", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")

        # Make the context current
        glfw.make_context_current(self.window)

        # Load shader program and set OpenGL parameters
        self.shader = ShaderLoader.load_shader_program(
            'shaders_src/vertex_src.txt',
            'shaders_src/fragment_src.txt'
        )
        glUseProgram(self.shader)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_DEPTH_TEST)

    def update_model(self):
        if self.model_setup is None or self.model_setup.model_indices is None:
            return

        # Set up perspective projection matrix
        projection = pyrr.matrix44.create_perspective_projection_matrix(
            self.pov,
            self.window_width / self.window_height,
            self.near,
            self.far
        )

        # Set the viewport based on window dimensions
        glViewport(0, 0, self.window_width, self.window_height)

        # Get the locations of shader variables
        model_loc = glGetUniformLocation(self.shader, "model")
        proj_loc = glGetUniformLocation(self.shader, "projection")
        view_loc = glGetUniformLocation(self.shader, "view")

        # Set the projection matrix in the shader
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

        # Set up the model position (translation matrix)
        model_pos = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([0, -5, -250])
        )

        # Poll GLFW for user inputs
        glfw.poll_events()

        # Clear the color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Rotate the model around the Y-axis over time
        rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())

        # Combine rotation and translation to get the model matrix
        model = pyrr.matrix44.multiply(rot_y, model_pos)

        # Bind the vertex array object and texture
        glBindVertexArray(self.model_setup.VAO)
        glBindTexture(GL_TEXTURE_2D, self.model_setup.textures)

        # Draw the model using triangles
        glDrawArrays(GL_TRIANGLES, 0, len(self.model_setup.model_indices))

        # Set up the view matrix (camera position and orientation)
        view = pyrr.matrix44.create_look_at(
            pyrr.Vector3([0, 0, 8]),
            pyrr.Vector3([0, 0, 0]),
            pyrr.Vector3([0, 1, 0])
        )

        # Set the view and model matrices in the shader
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

        # Swap the front and back buffers to display the rendered image
        glfw.swap_buffers(self.window)

    # TODO
    def draw_background(self):
        pass

    def capture_frame(self):
        # Create an array to store the pixel data
        data = glReadPixels(0, 0, self.window_width, self.window_height,
                            GL_BGRA, GL_UNSIGNED_BYTE)

        # Convert the pixel data to a NumPy array
        return np.frombuffer(data, dtype=np.uint8).reshape(
            self.window_height, self.window_width, 4
        )

    def run(self, window_width, window_height):
        self.window_width, self.window_height = window_width, window_height

        # Set the context window size
        glfw.set_window_size(self.window, window_width, window_height)

        # Constantly update the model
        self.update_model()

        return self.capture_frame()


# For testing purposes
if __name__ == "__main__":
    import cv2

    # Set initial parameters
    pov, near, far, frame_width, frame_height = 45, 0.1, 1000, 1280, 720

    # Load model and background
    model_file = "models/pure_democracy.obj"
    model_texture_file = "models/pure_democracy.png"
    background = "media/robots.webp"

    # Create an instance of OpenGLContext and initialize OpenGL parameters
    context = OpenGLContext(pov, near, far, frame_width, frame_height)

    # Create an instance of ModelSetup and pass it to the context
    model_setup = ModelSetUp(model_file, model_texture_file)
    context.model_setup = model_setup

    # Create opencv window and set its size
    cv2.namedWindow("OpenCV Frame", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("OpenCV Frame", frame_width, frame_height)

    # Initialize the loop,
    # window size can be changed by dragging only the opencv window
    while not glfw.window_should_close(context.window):
        window_size = cv2.getWindowImageRect("OpenCV Frame")
        frame_width, frame_height = window_size[2], window_size[3]

        # Run the context and get the frame
        frame = context.run(frame_width, frame_height)
        frame = cv2.flip(frame, 0)

        # glfw.show_window(context.window)
        cv2.imshow("OpenCV Frame", frame)
