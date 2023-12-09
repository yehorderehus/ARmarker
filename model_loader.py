import numpy as np


class ModelLoader:
    buffer = []

    @staticmethod
    def search_data(data_values, coordinates, skip, data_type):
        for d in data_values:
            if d == skip:
                continue
            if data_type == 'float':
                coordinates.append(float(d))
            elif data_type == 'int':
                coordinates.append(int(d)-1)

    @staticmethod  # Sorted vertex buffer for use with glDrawArrays
    def create_sorted_vertex_buffer(indices_data, vertices, textures, normals):
        for i, ind in enumerate(indices_data):
            if i % 3 == 0:  # Sort the vertex coordinates
                start = ind * 3
                end = start + 3
                ModelLoader.buffer.extend(vertices[start:end])
            elif i % 3 == 1:  # Sort the texture coordinates
                start = ind * 2
                end = start + 2
                ModelLoader.buffer.extend(textures[start:end])
            elif i % 3 == 2:  # Sort the normal vectors
                start = ind * 3
                end = start + 3
                ModelLoader.buffer.extend(normals[start:end])

    @staticmethod  # TODO Unsorted vertex buffer for use with glDrawElements
    def create_unsorted_vertex_buffer(indices_data, vertices,
                                      textures, normals):
        num_verts = len(vertices) // 3

        for i1 in range(num_verts):
            start = i1 * 3
            end = start + 3
            ModelLoader.buffer.extend(vertices[start:end])

            for i2, data in enumerate(indices_data):
                if i2 % 3 == 0 and data == i1:
                    start = indices_data[i2 + 1] * 2
                    end = start + 2
                    ModelLoader.buffer.extend(textures[start:end])

                    start = indices_data[i2 + 2] * 3
                    end = start + 3
                    ModelLoader.buffer.extend(normals[start:end])

                    break

    @staticmethod
    def show_buffer_data(buffer):
        for i in range(len(buffer)//8):
            start = i * 8
            end = start + 8
            print(buffer[start:end])

    @staticmethod
    def load_model(file, sorted=True):
        vert_coords = []  # Has to contain the vertex coordinates
        tex_coords = []  # Has to contain the texture coordinates
        norm_coords = []  # Has to contain the vertex normals
        all_indices = []  # Has to contain the vertex, texture, normal indices
        indices = []  # Has to contain the indices for indexed drawing

        with open(file, 'r') as f:
            line = f.readline()
            while line:
                values = line.split()

                # Check if values list is not empty before indexing
                if values:
                    if values[0] == 'v':
                        ModelLoader.search_data(values, vert_coords,
                                                'v', 'float')
                    elif values[0] == 'vt':
                        ModelLoader.search_data(values, tex_coords,
                                                'vt', 'float')
                    elif values[0] == 'vn':
                        ModelLoader.search_data(values, norm_coords,
                                                'vn', 'float')
                    elif values[0] == 'f':
                        for value in values[1:]:
                            val = value.split('/')
                            ModelLoader.search_data(val, all_indices,
                                                    'f', 'int')
                            indices.append(int(val[0]) - 1)

                line = f.readline()

        if sorted:
            # Use with glDrawArrays
            ModelLoader.create_sorted_vertex_buffer(all_indices, vert_coords,
                                                    tex_coords, norm_coords)
        else:
            # Use with glDrawElements
            ModelLoader.create_unsorted_vertex_buffer(all_indices, vert_coords,
                                                      tex_coords, norm_coords)

        # Create a local copy of the buffer list,
        # otherwise it will overwrite the static field buffer
        buffer = ModelLoader.buffer.copy()

        # After the copy, make sure to set it back to an empty list
        ModelLoader.buffer = []

        return np.array(indices, dtype='uint32'), np.array(buffer,
                                                           dtype='float32')
