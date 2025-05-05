# A small 3D demo using pyxel made in ca. 6 hours without searching anything
# online (only having some doc on paper) without having used pyxel before.
#
# Note: This version contains bug fixes made afterwards.
#
# This software is licensed under the BSD-3-Clause license:
#
# Copyright 2025 Mibi88
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# BUGS
# Camera.__rotate_x is not working correctly

import pyxel
import time

WIDTH = 256
HEIGHT = 256

class Camera:
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0
        self.rx, self.ry, self.rz = 0, 0, 0
        self.__fov = 80
    def project(self, x: float, y: float, z: float) -> tuple:
        if not z: z = 0.0001
        a = self.__fov/2
        tan_a = pyxel.sin(a)/pyxel.cos(a)
        f = WIDTH/(2*tan_a)
        m = f/z
        return (x*m+WIDTH/2, y*m+HEIGHT/2)
    def __rotate_x(self, x: float, y: float, z: float, a: float) -> tuple:
        ry = y*pyxel.cos(a)-z*pyxel.sin(a)
        rz = y*pyxel.sin(a)+z*pyxel.cos(a)
        return (x, ry, rz)
    def __rotate_y(self, x: float, y: float, z: float, a: float) -> tuple:
        rz = z*pyxel.cos(a)-x*pyxel.sin(a)
        rx = z*pyxel.sin(a)+x*pyxel.cos(a)
        return (rx, y, rz)
    def __rotate_z(self, x: float, y: float, z: float, a: float) -> tuple:
        rx = x*pyxel.cos(a)-y*pyxel.sin(a)
        ry = x*pyxel.sin(a)+y*pyxel.cos(a)
        return (rx, ry, z)
    def rotate(self, x: float, y: float, z: float, ax: float, ay: float,
               az: float) -> tuple:
        x, y, z = self.__rotate_x(x, y, z, ax)
        x, y, z = self.__rotate_y(x, y, z, ay)
        x, y, z = self.__rotate_z(x, y, z, az)
        return (x, y, z)
    def transform(self, x: float, y: float, z: float) -> tuple:
        x -= self.x
        y -= self.y
        z -= self.z
        x, y, z = self.rotate(x, y, z, self.rx, self.ry, self.rz)
        return (x, y, z)

class Model:
    def __init__(self, indices: list, colors: list, vertices: list):
        self.__indices = indices
        self.__colors = colors
        self.__vertices = vertices
    def update(self, indices: list, colors: list, vertices: list):
        self.__indices = indices
        self.__colors = colors
        self.__vertices = vertices
    def get_copy(self) -> tuple:
        return ([i for i in self.__indices], [i for i in self.__colors],
                [i for i in self.__vertices])

class Entity:
    def __init__(self, model: Model):
        self.model = model
        self.x, self.y, self.z = 0, 0, 0
        self.rx, self.ry, self.rz = 0, 0, 0

class Renderer:
    def __init__(self):
        self.camera = Camera()
        self.entities = []
    def render(self) -> None:
        indices, colors, vertices = [], [], []
        a = 0
        for n in self.entities:
            idx, c, v = n.model.get_copy()
            # Transform the vertices
            for i in range(len(v)):
                x, y, z = v[i]
                x, y, z = self.camera.rotate(x, y, z, n.rx, n.ry, n.rz)
                x += n.x
                y += n.y
                z += n.z
                v[i] = x, y, z
                v[i] = self.camera.transform(x, y, z)
            idx = [(e[0]+a, e[1]+a, e[2]+a) for e in idx]
            indices += idx
            a += len(v)
            vertices += v
            colors += c
        self.__render_from_arrays(vertices, indices, colors)
    def __triangle_depth(self, vertices: list, indices: tuple) -> float:
        v1 = vertices[indices[0]]
        v2 = vertices[indices[1]]
        v3 = vertices[indices[2]]
        # Calculate the depth of the triangle
        return (v1[2]+v2[2]+v3[2])/3
    def __render_from_arrays(self, vertices: list, indices: list,
                             colors: list):
        for i in range(len(indices)):
            m = self.__triangle_depth(vertices, indices[i])
            p = i
            for n in range(i+1, len(indices)):
                z = self.__triangle_depth(vertices, indices[n])
                if z > m:
                    p = n
                    m = z
            tmp = indices[i]
            c = colors[i]
            indices[i] = indices[p]
            colors[i] = colors[p]
            indices[p] = tmp
            colors[p] = c
        
        for i in range(len(indices)):
            v1 = vertices[indices[i][0]]
            v2 = vertices[indices[i][1]]
            v3 = vertices[indices[i][2]]
            
            if v1[2] >= 0 and v2[2] >= 0 and v3[2] >= 0:
                v1 = self.camera.project(v1[0], v1[1], v1[2])
                v2 = self.camera.project(v2[0], v2[1], v2[2])
                v3 = self.camera.project(v3[0], v3[1], v3[2])
                
                if (v1[0] < 0 or v1[1] < 0 or v1[0] > WIDTH or
                    v1[1] > HEIGHT or
                    v2[0] < 0 or v2[1] < 0 or v2[0] > WIDTH or
                    v2[1] > HEIGHT or
                    v3[0] < 0 or v3[1] < 0 or v3[0] > WIDTH or
                    v3[1] > HEIGHT):
                    continue
                
                pyxel.tri(v1[0], v1[1], v2[0], v2[1], v3[0], v3[1], colors[i])
    def add(self, entity: Entity):
        self.entities.append(entity)

class Terrain:
    def __init__(self, seed: int):
        self._seed = seed
    def generate(self, sx: int, sy: int, w: int, h: int) -> tuple:
        vertices = []
        indices = []
        pyxel.nseed(self._seed)
        for y in range(h):
            for x in range(w):
                vertices.append((x, y, pyxel.noise((x+sx)/2, (y+sy)/2)))
                if x > 1 and y > 1:
                    indices += [
                        (y*w+x, y*w+x-1, y*w+x-w),
                        (y*w+x-1, y*w+x-w, y*w+x-w-1)
                    ]
        return (vertices, indices)

class TerrainHandler:
    def __init__(self, w: int, h: int, cw: int, ch: int, seed: int):
        self.terrain = []
        self.terrain_pos = []
        self._w, self._h, self._cw, self._ch = w, h, cw, ch
        self._cx, self._cy = 0, 0
        self._seed = seed
        for y in range(h):
            for x in range(w):
                self.terrain_pos.append((x*cw, y*ch))
                self.terrain.append(Terrain(seed).generate(-x*cw, -y*ch, cw,
                                                           ch))
    def update(self, x: int, y: int):
        
        cx = x//self._cw*self._cw-self._cw*(self._w/2)
        cy = y//self._ch*self._ch-self._ch*(self._h/2)
        if self._cx == cx and self._cy == cy:
            return
        
        self.terrain = []
        self.terrain_pos = []
        
        # TODO: Only regenerate the map partially
        for y in range(self._h):
            for x in range(self._w):
                self.terrain_pos.append((cx+x*self._cw, cy+y*self._ch))
                self.terrain.append(Terrain(self._seed)
                                    .generate(cx-x*self._cw, cy-y*self._ch,
                                              self._cw, self._ch))
        self._cx, self._cy = cx, cy

pyxel.init(WIDTH, HEIGHT, title = "3D")

vertices = [
    (1, 1, -1),
    (1, -1, -1),
    (1, 1, 1),
    (1, -1, 1),
    (-1, 1, -1),
    (-1, -1, -1),
    (-1, 1, 1),
    (-1, -1, 1)
]

indices = [
    (4, 2, 0),
    (2, 7, 3),
    (6, 5, 7),
    (1, 7, 5),
    (0, 3, 1),
    (4, 1, 5),
    (4, 6, 2),
    (2, 6, 7),
    (6, 4, 5),
    (1, 3, 7),
    (0, 2, 3),
    (4, 0, 1)
]

colors = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12
]

terrain = Terrain(1024)
terrain_v, terrain_i = terrain.generate(0, 0, 16, 16)

c = [i%15+1 for i in range(len(terrain_i))]

"""
terrain_handler = TerrainHandler(3, 3, 4, 4, 1024)

v = []
for n in terrain_handler.terrain: v += n[0]
i = []
for n in terrain_handler.terrain: v += n[1]

c = [i%15+1 for i in range(len(i))]
"""

renderer = Renderer()
camera = Camera()
model = Model(terrain_i, c, terrain_v)
entity = Entity(model)
entity.y = 4
entity.x = 0
entity.rx = 90
renderer.camera.z = -8

cube_model = Model(indices, colors, vertices)
cube = Entity(cube_model)

cube.z = 4

renderer.add(cube)

renderer.add(entity)

def draw():
    pyxel.cls(0)
    renderer.render()

MAP_W = 24
MAP_H = 24

SPEED = 1

last = time.time()

def update():
    global last
    new = time.time()
    delta = (last-new)*30
    print(delta)
    last = new
    if pyxel.btn(pyxel.KEY_UP):
        renderer.camera.z += pyxel.cos(-renderer.camera.ry)*SPEED*delta
        renderer.camera.x += pyxel.sin(-renderer.camera.ry)*SPEED*delta
    if pyxel.btn(pyxel.KEY_DOWN):
        renderer.camera.z -= pyxel.cos(-renderer.camera.ry)*SPEED*delta
        renderer.camera.x -= pyxel.sin(-renderer.camera.ry)*SPEED*delta
    if pyxel.btn(pyxel.KEY_LEFT):
        renderer.camera.ry -= 2*delta
    if pyxel.btn(pyxel.KEY_RIGHT):
        renderer.camera.ry += 2*delta
    
    """
    terrain_handler.update(renderer.camera.x, renderer.camera.z)
    
    v = []
    for n in terrain_handler.terrain: v += n[0]
    i = []
    for n in terrain_handler.terrain: i += n[1]
    #print(len(terrain_handler.terrain))
    
    #print(i, v)
    
    c = [i%15+1 for i in range(len(i))]
    """
    
    """
    v, i = terrain.generate(-int(renderer.camera.x)-MAP_W/2,
                            -int(renderer.camera.z)-MAP_H/2, MAP_W, MAP_H)
    #print(v, i)
    entity.x, entity.z = int(renderer.camera.x)-MAP_W/2,
                         int(renderer.camera.z)-MAP_H/2

    c = [(int(renderer.camera.y)*MAP_W+int(renderer.camera.x)+i)%15+1
         for i in range(len(i))]
    
    model.update(i, c, v)
    """
    
    """
    entity.x = int((renderer.camera.x-MAP_W/2)//MAP_W*MAP_W)
    entity.z = int((renderer.camera.z-MAP_H/2)//MAP_H*MAP_H)
    
    v, i = terrain.generate(entity.x, entity.z, MAP_W, MAP_H)
    """
    
    cube.rz -= 1*delta
    cube.ry += 1*delta
        

pyxel.run(update, draw)

