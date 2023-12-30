from PIL import Image
from OpenGL.GL import *

# Common import
from obj_loader import ObjLoader

class ModelSetUp:
    def __init__(self) -> None:
        # Model parameters
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.model_indices = None
        self.model_buffer = None

        # Texture parameters
        self.model_textures = glGenTextures(1)

    def upload_model(self, file=None, texture_file=None):
        if file:
            self.model_loader(file)
        if texture_file:
            self.texture_loader(texture_file, self.model_textures)

    def model_loader(self, path):
        # TODO - Add and handle support for various file formats
        self.model_indices, self.model_buffer = ObjLoader.load_obj(path)

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

    def texture_loader(self, path, texture):
        glBindTexture(GL_TEXTURE_2D, texture)

        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Set the texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Load image
        image = Image.open(path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Convert image to bytes
        image_data = image.convert("RGBA").tobytes()

        # Load image data into the texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height,
                    0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)