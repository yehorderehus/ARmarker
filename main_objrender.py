# OpenGL imports
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

# Other imports
import glfw
import pyrr

# Common imports
from main_objtexloader import load_texture
from main_objloader import ObjLoader
from main import ARmarkerEngine

class ShaderLoader:
    @staticmethod
    def read_shader_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    
    @staticmethod
    def load_shader_program(vertex_src_path, fragment_src_path):
        vertex_src = ShaderLoader.read_shader_file(vertex_src_path)
        fragment_src = ShaderLoader.read_shader_file(fragment_src_path)
        return compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                              compileShader(fragment_src, GL_FRAGMENT_SHADER))


class ObjectSetup:
    def __init__(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.textures = glGenTextures(1)
        self.model_indices = None
        self.model_buffer = None

    def model_loader(self):
        self.model_indices, self.model_buffer = ObjLoader.load_model("objects/pure_democracy.obj")

        # Load the model textures - can be commented out if not needed
        load_texture("objects/pure_democracy.png", self.textures)

    def model_parameters(self):

        # Model VAO
        glBindVertexArray(self.VAO)

        # Model VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.model_buffer.nbytes, self.model_buffer, GL_STATIC_DRAW)

        # Model vertices
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.model_buffer.itemsize * 8, ctypes.c_void_p(0))

        # Model textures
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.model_buffer.itemsize * 8, ctypes.c_void_p(12))

        # Model normals
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, self.model_buffer.itemsize * 8, ctypes.c_void_p(20))
        glEnableVertexAttribArray(2)

    def setup(self):
        self.model_loader()
        self.model_parameters()


class OpenGLContext:
    def __init__(self):
        if not glfw.init():
            raise Exception("glfw can not be initialized!")
        
        # Set values for the context projection and initial values for window
        self.pov = 45
        self.near = 0.1
        self.far = 1000 # increase this value if the object is not visible
        self.window_width = 1280
        self.window_height = 720

        # Set window, hidden initially
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)   
        self.window = glfw.create_window(self.window_width, self.window_height, "Viewer", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")
        
        # Set window position, size and callback function for window resize
        glfw.set_window_pos(self.window, 400, 200)
        glfw.set_window_size_callback(self.window, self.window_resize)
        glfw.make_context_current(self.window)

    def window_resize(self, window, width, height):  # update viewport, projection matrix and projection location
        glViewport(0, 0, width, height)
        projection = self.update_projection(self.pov, width, height, self.near, self.far)
        glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, projection)

    def update_projection(self, pov, window_width, window_height, near, far):
        # fov, aspect ratio, near and far clipping plane
        return pyrr.matrix44.create_perspective_projection_matrix(pov, window_width / window_height, near, far)

    def prepare(self):
        glUseProgram(self.shader)
        glClearColor(0.1, 0.1, 0.1, 1)  # background color
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Create the projection and view matrix
        projection = self.update_projection(self.pov, self.window_width, self.window_height, self.near, self.far)
        view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 0, 8]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))  ## I suggest values in this vectors will be variables and will depend on opencv

        # Get the locations of the model, view and projection matrices
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.model_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, -5, -250]))  # last number is the distance from the camera, CONFIGURE DEPENDING ON THE OBJECT

        self.proj_loc = glGetUniformLocation(self.shader, "projection")
        glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, projection)

        view_loc = glGetUniformLocation(self.shader, "view")
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    
    def draw(self):
        glfw.poll_events()  # poll GLFW for user inputs

        # Clear the color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Create the rotation matrix and multiply it with the model matrix
        rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())
        model = pyrr.matrix44.multiply(rot_y, self.model_pos)

        # Draw the model
        glBindVertexArray(self.object_setup.VAO)
        glBindTexture(GL_TEXTURE_2D, self.object_setup.textures)
        glDrawArrays(GL_TRIANGLES, 0, len(self.object_setup.model_indices))

        # Update the model matrix
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, model)

        # Swap front and back buffers
        glfw.swap_buffers(self.window)

    def run(self, object_setup):
        self.object_setup = object_setup  # pass the object setup parameters to the context
        glfw.show_window(self.window)  # show the initially hidden window
        self.prepare()
        while not glfw.window_should_close(self.window):
            self.draw()
        glfw.terminate()


if __name__ == "__main__":
    # Create an instance of OpenGLContext
    context = OpenGLContext()

    # Load the shader program
    context.shader = ShaderLoader.load_shader_program('shaders_src/vertex_src.txt', 'shaders_src/fragment_src.txt')

    # Create an instance of ObjectSetup and call setup
    object_setup = ObjectSetup()
    object_setup.setup()

    # Run the viewer - can be commented out if not needed
    context.run(object_setup)

    ## Still don't know which parts of the code are needed only for displaying, and which parts are needed to load the object