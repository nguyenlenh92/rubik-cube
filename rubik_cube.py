import pygame
import numpy as np
import math

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SPEED = 0.3

# YELLOW = (255, 255, 0)
# YELLOW_FACE = 0

# BLUE = (0, 0, 255)
# BLUE_FACE = 1

# WHITE = (255, 255, 255)
# WHITE_FACE = 2

# GREEN = (0, 255, 0)
# GREEN_FACE = 3

# ORANGE = (255, 165, 0)
# ORANGE_FACE = 4

# RED = (255, 0, 0)
# RED_FACE = 5



BLACK = (0, 0, 0)

VERTICES = [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1)]
FACES = [(0, 1, 2, 3), (1, 5, 6, 2), (5, 4, 7, 6), # yellow, blue, white, green, orange, red
         (4, 0, 3, 7), (3, 2, 6, 7), (1, 0, 4, 5)]
CUBE_ORIGIN = [(-1, -1, 0), (0, -1, 0), (1, -1, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (-1, 1, 0), (-1, 0, 0),
               (-1, -1, 1), (0, -1, 1), (1, -1, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1), (-1, 1, 1), (-1, 0, 1), (0, 0, 1),
               (-1, -1, -1), (0, -1, -1), (1, -1, -1), (1, 0, -1), (1, 1, -1), (0, 1, -1), (-1, 1, -1), (-1, 0, -1), (0, 0, -1)]


COLORS = {
    FACES[0]: (255, 255, 0),
    FACES[1]: (0, 0, 255),
    FACES[2]: (255, 255, 255),
    FACES[3]: (0, 255, 0),
    FACES[4]: (255, 165, 0),
    FACES[5]: (255, 0, 0)
}

def project(vector, w, h, fov, distance):
    factor = math.atan(fov / 2 * math.pi / 180) / (distance + vector.z)
    x = vector.x * factor * w + w / 2
    y = -vector.y * factor * w + h / 2
    return pygame.math.Vector3(x, y, vector.z)


def rotate_vertices(vertices, angle, axis):
    return [v.rotate(angle, axis) for v in vertices]


def scale_vertices(vertices, s):
    return [pygame.math.Vector3(v[0]*s[0], v[1]*s[1], v[2]*s[2]) for v in vertices]


def translate_vertices(vertices, t):
    return [v + pygame.math.Vector3(t) for v in vertices]


def project_vertices(vertices, w, h, fov, distance):
    return [project(v, w, h, fov, distance) for v in vertices]


class Mesh():

    def __init__(self, vertices, faces):
        self.__vertices = [pygame.math.Vector3(v) for v in vertices]
        self.__faces = faces

    def rotate(self, angle, axis):
        self.__vertices = rotate_vertices(self.__vertices, angle, axis)

    def scale(self, s):
        self.__vertices = scale_vertices(self.__vertices, s)

    def translate(self, t):
        self.__vertices = translate_vertices(self.__vertices, t)

    def calculate_average_z(self, vertices):
        return [(i, sum([vertices[j].z for j in f]) / len(f)) for i, f in enumerate(self.__faces)]

    def get_face(self, index):
        return self.__faces[index]

    def get_vertices(self):
        return self.__vertices

    def create_polygon(self, face, vertices):
        return [(vertices[i].x, vertices[i].y) for i in [*face, face[0]]]

    def get_color(self):
        return self.__color

    def set_color(self, color):
        self.__color = color




class Scene:
    def __init__(self, meshes, fov, distance):
        self.meshes = meshes
        self.fov = fov
        self.distance = distance
        self.euler_angles = [0, 0, 0]

    def transform_vertices(self, vertices, width, height):
        transformed_vertices = vertices
        axis_list = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        for angle, axis in reversed(list(zip(list(self.euler_angles), axis_list))):
            transformed_vertices = rotate_vertices(
                transformed_vertices, angle, axis)
        transformed_vertices = project_vertices(
            transformed_vertices, width, height, self.fov, self.distance)
        return transformed_vertices

    def draw(self, surface):

        polygons = []
        for mesh in self.meshes:
            transformed_vertices = self.transform_vertices(mesh.get_vertices(), *surface.get_size())
            avg_z = mesh.calculate_average_z(transformed_vertices)
            for z in avg_z:
                pointlist = mesh.create_polygon(mesh.get_face(z[0]), transformed_vertices)
                self.assign_color(mesh.get_face(z[0]), mesh)
                polygons.append((pointlist, z[1], mesh.get_color()))

        for poly in sorted(polygons, key=lambda x: x[1], reverse=True):
            pygame.draw.polygon(surface, poly[2], poly[0])
            pygame.draw.polygon(surface, BLACK, poly[0], 3)

    def assign_color(self, face, mesh):
        mesh.set_color(COLORS[face])
    
    def assign_color_custom(self, color, mesh):
        mesh.set_color(color)
    



class Cube:
    def __init__(self, vertices, faces, cube_origins):
        self.vertices = vertices
        self.faces = faces
        self.cube_origins = cube_origins
        self.meshes = []

        for origin in self.cube_origins:               
            cube = Mesh(self.vertices, self.faces)
            cube.scale((0.5, 0.5, 0.5))
            cube.translate(origin)
            self.meshes.append(cube)


class Game:
    def __init__(self):
        pygame.init()
        self.CubeObj = Cube(VERTICES, FACES, CUBE_ORIGIN)
        self.window = pygame.display.set_mode(size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()
        self.scene = Scene(self.CubeObj.meshes, 90, 10)
    
    def update(self):
        self.clock.tick(1000)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEMOTION:
                mouses = pygame.mouse.get_pressed()
                mouse_pos = pygame.mouse.get_rel()

                if mouses[0]:
                    self.scene.euler_angles[1] -= mouse_pos[0] * SPEED
                    self.scene.euler_angles[0] -= mouse_pos[1] * SPEED


        self.window.fill(BLACK)
        self.scene.draw(GameObj.window)
        pygame.display.flip()


if __name__ == "__main__":
    GameObj = Game()
    while GameObj.running:
        GameObj.update()
        
    pygame.quit()
    exit()
