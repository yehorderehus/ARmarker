from OpenGL.GL import *
import glfw
import pyrr
import numpy as np
from PIL import Image

# Common imports
from shader_loader import ShaderLoader
from model_setup import ModelSetUp


class OpenGLContext:
    def __init__(self):
        if not glfw.init():
            raise Exception("glfw can not be initialized!")

        # Set window with TEMP size, HIDDEN by default
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        self.window = glfw.create_window(1, 1,
                                         "OpenGL Context", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")

        # Make the context current
        glfw.make_context_current(self.window)

        # Load shader program
        self.shader = ShaderLoader.load_shader_program(
            'shaders_src/vertex_src.txt',
            'shaders_src/fragment_src.txt'
        )

        # Set up OpenGL parameters
        glUseProgram(self.shader)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_DEPTH_TEST)
        
        # Initialize model setup
        self.model_setup = ModelSetUp()

        # Assign scene texture
        self.scene_textures = glGenTextures(1)

    def update_window(self):
        # Set the viewport size
        glViewport(0, 0, self.scene_width, self.scene_height)

        # Set up perspective projection matrix
        projection = pyrr.matrix44.create_perspective_projection_matrix(
            self.pov,
            self.scene_width / self.scene_height,
            self.near,
            self.far
        )

        # Set the projection matrix in the shader
        proj_loc = glGetUniformLocation(self.shader, "projection")
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

        # Get the locations of shader variables
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.view_loc = glGetUniformLocation(self.shader, "view")

        # Update the window size
        glfw.set_window_size(self.window, self.scene_width, self.scene_height)
        print("Window size updated to: ", self.scene_width, self.scene_height)

    def draw_model(self):
        if self.model_setup is None or self.model_setup.model_indices is None \
        or self.model_setup.model_buffer is None:
            return

        # Rotate the model around the Y-axis over time
        rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())

        # Set up the model position (translation matrix)
        model_pos = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([0, -5, -250])
        )

        # Combine rotation and translation to get the model matrix
        model = pyrr.matrix44.multiply(rot_y, model_pos)

        # Set up the view matrix (camera position and orientation)
        view = pyrr.matrix44.create_look_at(
            pyrr.Vector3([0, 0, 8]),
            pyrr.Vector3([0, 0, 0]),
            pyrr.Vector3([0, 1, 0])
        )

        # Set the view and model matrices in the shader
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, model)

        # Bind the vertex array object and texture
        glBindVertexArray(self.model_setup.VAO)
        glBindTexture(GL_TEXTURE_2D, self.model_setup.model_textures)

        # Draw the model using triangles
        glDrawArrays(GL_TRIANGLES, 0, len(self.model_setup.model_indices))

    # TODO - Does not work
    def draw_scene(self):
        if self.scene is None:
            return

        # Load the scene texture
        self.scene_loader()
 
        # Draw the scene
        glBindTexture(GL_TEXTURE_2D, self.scene_textures)
        glPushMatrix()
        glTranslatef(0.0, 0.0, -10.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(-1.0, -1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(1.0, -1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(1.0, 1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(-1.0, 1.0)
        glEnd()
        glPopMatrix()

    def scene_loader(self):
        glBindTexture(GL_TEXTURE_2D, self.scene_textures)

        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Read image
        image = Image.fromarray(np.array(self.scene))

        # Convert image to bytes
        image_data = image.convert("RGBA").tobytes()

        # Load image data into the texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height,
                    0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    def capture_frame(self):
        # Create an array to store the pixel data
        data = glReadPixels(0, 0, self.scene_width, self.scene_height,
                            GL_BGRA, GL_UNSIGNED_BYTE)

        # Convert the pixel data to a NumPy array
        return np.frombuffer(data, dtype=np.uint8).reshape(
            self.scene_height, self.scene_width, 4
        )

    def scene_params(self, frame, pov, near, far):
        self.scene = frame
        self.scene_width = frame.shape[1]
        self.scene_height = frame.shape[0]
        self.pov, self.near, self.far = pov, near, far

    def run(self, frame, pov, near, far):
        # Calculate frame width and height
        self.scene_params(frame, pov, near, far)

        # Update the window if needed
        current_width, current_height = glfw.get_window_size(self.window)
        if current_width != self.scene_width or current_height != self.scene_height:
            self.update_window()

        # Process events
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Call draw functions
        self.draw_scene()
        self.draw_model()

        # Swap the buffers
        glfw.swap_buffers(self.window)
        
        return self.capture_frame()


# For testing purposes
if __name__ == "__main__":
    import cv2

    # Set initial parameters
    pov, near, far = 45, 0.1, 1000
    frame = cv2.imread("media/marker.png")
    model_file = "models/pure_democracy.obj"
    model_texture_file = "models/pure_democracy.png"

    # Create an instance of OpenGLContext and initialize OpenGL parameters
    context = OpenGLContext()

    # Upload or change the model (optional)
    context.model_setup.upload_model(model_file, model_texture_file)

    # Create opencv window and set its size
    cv2.namedWindow("OpenCV Frame")

    # Initialize the loop
    while not glfw.window_should_close(context.window):
        output = context.run(frame, pov, near, far)

        # Flip the frame vertically (realized in frame_to_texture)
        output = cv2.flip(output, 0)

        # Update the opencv window
        cv2.resizeWindow("OpenCV Frame", frame.shape[1], frame.shape[0])
        cv2.imshow("OpenCV Frame", output)

        # Show the OpenGL window
        # glfw.show_window(context.window)
