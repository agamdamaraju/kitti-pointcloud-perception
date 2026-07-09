import numpy as np
import open3d as o3d

def load_kitti_bin(bin_path):
    point = np.fromfile(bin_path, dtype=np.float32).reshape(-1, 4)
    points_xyz = point[:, :3]
    intensity = point[:, 3]
    return points_xyz, intensity

def numpy_to_open3d(points_xyz):
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points_xyz)
    return point_cloud