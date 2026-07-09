import open3d as o3d

def visualize_cloud(point_cloud, window_name="Point Cloud"):
    o3d.visualization.draw_geometries(
        [point_cloud],
        window_name=window_name,
        width=1200,
        height=800
    )

def visualize_ground_removal(non_ground_cloud, ground_cloud):
    o3d.visualization.draw_geometries(
        [ground_cloud, non_ground_cloud],
        window_name="Ground Removal: Gray=Ground, Red=Objects",
        width=1200,
        height=800
    )