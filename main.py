import argparse
from src.loader import load_kitti_bin, numpy_to_open3d
from src.preprocess import crop_roi, voxel_downsample, remove_ground_plane
from src.visualize import visualize_cloud, visualize_ground_removal

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin_path", type=str, required=True)
    parser.add_argument("--voxel_size", type=float, default=0.15)
    parser.add_argument("--ground_threshold", type=float, default=0.2)
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

if __name__ == "__main__":
    main()