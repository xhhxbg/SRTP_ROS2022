# -*-coding:utf-8 -*-
import open3d as o3d
import numpy as np
import copy
import time
 
# 在原点创建坐标框架网格


group_index = 0

x0 = -2
y0 = 0
z0 = 0.1

mesh = o3d.geometry.TriangleMesh.create_coordinate_frame()
mesh_1 = copy.deepcopy(mesh)    




# 相对旋转四元数data[3, 7]
# R = mesh_1.get_rotation_matrix_from_quaternion((0, 0.707, 0.707, 0))
R = mesh_1.get_rotation_matrix_from_quaternion((0.5, -0.5, 0.5, -0.5))
mesh_1.rotate(R, center=(0, 0, 0))
# 相机固定旋转偏移
# R = mesh_1.get_rotation_matrix_from_xyz((0, -np.pi/2, np.pi/2))
# mesh_1.rotate(R, center=(0, 0, 0))
# 相对偏移data[7, 10]
# mesh_1.translate((x0+data[0], y0+data[1], z0+data[2]))
# mesh_1.translate((0.5, 0, 0))

o3d.visualization.draw_geometries([mesh, mesh_1])
