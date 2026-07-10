import numpy as np, open3d as o3d

def run_dbscan_clustering(point_cloud, eps=0.8, min_points=10):
    labels = np.array(point_cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))
    return labels

def color_clusters(point_cloud, labels):
    points = np.asarray(point_cloud.points)
    max_label = labels.max()

    print(f"Detected clusters: {max_label + 1}")
    print(f"Noise points: {np.sum(labels == -1)}")

    colors = np.zeros((points.shape[0], 3))

    if max_label >= 0:
        random_colors = np.random.rand(max_label + 1, 3)
        
        for cluster_id in range(max_label + 1):
            colors[labels == cluster_id] = random_colors[cluster_id]

    colors[labels == -1] = [0, 0, 0]

    clustered_cloud = o3d.geometry.PointCloud()
    clustered_cloud.points = o3d.utility.Vector3dVector(points)
    clustered_cloud.colors = o3d.utility.Vector3dVector(colors)

    return clustered_cloud

def extract_clusters(point_cloud, labels, min_cluster_points=20, max_cluster_points=5000):
    points = np.asarray(point_cloud.points)
    clusters = []

    unique_labels = sorted(set(labels))

    for cluster_id in unique_labels:
        if cluster_id == -1: continue
        clusters_indices = np.where(labels == cluster_id)[0]
        num_points = len(clusters_indices)

        if num_points < min_cluster_points or num_points > max_cluster_points: continue

        cluster_points = points[clusters_indices]

        cluster_cloud = o3d.geometry.PointCloud()
        cluster_cloud.points = o3d.utility.Vector3dVector(cluster_points)

        clusters.append(
            {
                "cluster_id": int(cluster_id),
                "num_points": int(num_points),
                "cluster_cloud": cluster_cloud
            }
        )

        print(f"Valid clusters after filtering: {len(clusters)}")
        return clusters