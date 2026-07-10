from src.loader import load_kitti_bin, numpy_to_open3d
from src.preprocess import crop_roi, voxel_downsample, remove_ground_plane
from src.visualize import visualize_cloud, visualize_ground_removal, visualize_clusters, visualize_bounding_boxes
from src.clustering import run_dbscan_clustering, color_clusters, extract_clusters
from src.detection import create_bounding_box_detections, print_detection_summary
import argparse, os, open3d as o3d

def main():
    os.makedirs("results", exist_ok=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--bin_path", type=str, required=True)
    parser.add_argument("--voxel_size", type=float, default=0.15)
    parser.add_argument("--ground_threshold", type=float, default=0.2)
    parser.add_argument("--dbscan_eps", type=float, default=0.8)
    parser.add_argument("--dbscan_min_points", type=int, default=10)
    args = parser.parse_args()

    print(f"Loading point cloud: {args.bin_path}")

    points_xyz, intensity = load_kitti_bin(args.bin_path)

    print(f"Raw points: {points_xyz.shape[0]}")

    raw_cloud = numpy_to_open3d(points_xyz)
    raw_cloud.paint_uniform_color([1.0, 1.0, 1.0])

    print(f"Visualizing raw point cloud...")
    visualize_cloud(raw_cloud, window_name="Raw KITTI Point Cloud")

    cropped_points = crop_roi(points_xyz)
    print(f"Points after ROI crop: {cropped_points.shape[0]}")

    cropped_cloud = numpy_to_open3d(cropped_points)
    cropped_cloud.paint_uniform_color([1.0, 1.0, 1.0])

    print("Visualizing cropped point cloud...")
    visualize_cloud(cropped_cloud, window_name="Cropped ROI Point Cloud")

    downsampled_cloud = voxel_downsample(cropped_cloud, voxel_size=args.voxel_size)
    print(f"Points after voxel downsampling: {len(downsampled_cloud.points)}")

    print("Visualizing downsampled point cloud...")

    visualize_cloud(downsampled_cloud, window_name="Voxel Downsampled Point Cloud")

    non_ground_cloud, ground_cloud, plane_model = remove_ground_plane(downsampled_cloud, distance_threshold=args.ground_threshold)

    print("Detected ground plane equation:")
    print(plane_model)

    print(f"Ground points: {len(ground_cloud.points)}")
    print(f"Non-ground points: {len(non_ground_cloud.points)}")

    print("Visualizing ground removal result...")
    visualize_ground_removal(non_ground_cloud, ground_cloud)

    o3d.io.write_point_cloud("results/non_ground_cloud_002000.ply", non_ground_cloud)
    print("Saved non-ground cloud to results/non_ground_cloud_002000.ply")

    print("Running DBSCAN clustering on non-ground points...")
    labels = run_dbscan_clustering(non_ground_cloud, eps=args.dbscan_eps, min_points=args.dbscan_min_points)

    clustered_cloud = color_clusters(non_ground_cloud, labels)

    print("Visualizing DBSCAN clusters...")
    visualize_clusters(clustered_cloud)

    o3d.io.write_point_cloud("results/clustered_cloud_002000.ply", clustered_cloud)
    print("Saved clustered cloud to results/clustered_cloud_002000.ply")

    clusters = extract_clusters(non_ground_cloud, labels, min_cluster_points=8, max_cluster_points=1000)

    for cluster in clusters[:10]:
        print(
            f"Cluster {cluster['cluster_id']}: "
            f"{cluster['num_points']} points"
        )
    
    print("Creating 3D bounding boxes for valid clusters...")
    detections, bbox_geometries = create_bounding_box_detections(clusters)
    print_detection_summary(detections)

    if len(bbox_geometries) > 0:
        print("Visualizing clusters with 3D bounding boxes...")
        visualize_bounding_boxes(bbox_geometries)
    else:
        print("No valid bounding boxes to visualize after filtering.")

if __name__ == "__main__":
    main()