import numpy as np
import open3d as o3d

def crop_roi(points_xyz, x_range=(0,70), y_range=(-40,40), z_range=(-3,3)):
    x, y, z = points_xyz[:,0], points_xyz[:, 1], points_xyz[:, 2]
    mask = (
        (x >= x_range[0]) & (x <= x_range[1]) &
        (y >= y_range[0]) & (y <= y_range[1]) &
        (z >= z_range[0]) & (z <= z_range[1])
    )
    return points_xyz[mask]

def voxel_downsample(point_cloud, voxel_size=0.15):
    return point_cloud.voxel_down_sample(voxel_size=voxel_size)

def remove_ground_plane(point_cloud, distance_threshold=0.2, ransac_n=3, num_iteration=1000):
    plane_model, inliers = point_cloud.segment_plane(
        distance_threshold=distance_threshold,
        ransac_n=ransac_n,
        num_iterations=num_iteration
    )
    ground_cloud = point_cloud.select_by_index(inliers)
    non_ground_cloud = point_cloud.select_by_index(inliers, invert=True)
    
    ground_cloud.paint_uniform_color([0.5, 0.5, 0.5])
    non_ground_cloud.paint_uniform_color([1.0, 0.0, 0.0])

    return non_ground_cloud, ground_cloud, plane_model