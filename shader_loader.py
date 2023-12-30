import os
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


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