# KITTI 3D Point Cloud Perception Pipeline

This project implements a 3D LiDAR point cloud processing pipeline using the KITTI autonomous driving dataset. The current version focuses on Day 1 development: loading raw KITTI Velodyne point clouds, visualizing them, cropping the region of interest, applying voxel downsampling, and removing the road surface using RANSAC-based ground plane segmentation.

The goal of this project is to build a compact perception pipeline that can later be extended with object clustering, bounding box estimation, BEV visualization, and ego-centric spatial analysis.

---

## Project Objective

The objective of this project is to process raw KITTI LiDAR point clouds and build a classical 3D perception pipeline for autonomous driving scenes.

The current Day 1 pipeline focuses on:

- Loading KITTI `.bin` Velodyne point cloud files
- Converting raw binary LiDAR data into NumPy arrays
- Converting NumPy XYZ coordinates into Open3D point clouds
- Cropping the point cloud to a useful driving region
- Applying voxel downsampling to reduce point density
- Removing the ground plane using RANSAC
- Visualizing ground and non-ground points separately

---

## Dataset

This project uses the KITTI Object Detection dataset, specifically the Velodyne LiDAR point cloud files.

Each KITTI `.bin` file stores LiDAR points in the following format:

```text
x, y, z, intensity
```

Where:

```text
x = forward distance from the ego vehicle
y = left/right distance from the ego vehicle
z = height
intensity = LiDAR return strength
```

For Day 1, the pipeline was tested on individual KITTI Velodyne frames.

---

## Day 1 Pipeline

The implemented Day 1 pipeline is:

```text
Raw KITTI .bin file
        ↓
Load binary LiDAR data using NumPy
        ↓
Extract XYZ coordinates and intensity values
        ↓
Convert XYZ points to Open3D point cloud
        ↓
Crop region of interest
        ↓
Apply voxel downsampling
        ↓
Estimate ground plane using RANSAC
        ↓
Separate ground and non-ground points
        ↓
Visualize results
```

---

## Implemented Features

### 1. KITTI Point Cloud Loader

KITTI Velodyne `.bin` files are raw binary files. Each point contains four `float32` values:

```text
[x, y, z, intensity]
```

The loader reads the file using NumPy:

```python
points = np.fromfile(bin_path, dtype=np.float32).reshape(-1, 4)

points_xyz = points[:, :3]
intensity = points[:, 3]
```

This separates the 3D coordinates from the intensity values.

---

### 2. NumPy to Open3D Conversion

After loading the XYZ coordinates, the NumPy array is converted into an Open3D point cloud:

```python
point_cloud = o3d.geometry.PointCloud()
point_cloud.points = o3d.utility.Vector3dVector(points_xyz)
```

This allows the point cloud to be visualized and processed using Open3D.

---

### 3. Region of Interest Cropping

The raw point cloud contains many points that may not be useful for near-field autonomous driving perception. A region of interest is applied to keep points in front of the ego vehicle and within a reasonable road area.

Default crop settings:

```python
x_range = (0, 70)
y_range = (-40, 40)
z_range = (-3, 3)
```

This keeps:

```text
0 to 70 meters in front of the vehicle
-40 to 40 meters left/right
-3 to 3 meters vertically
```

---

### 4. Voxel Downsampling

Voxel downsampling reduces the number of points while preserving the overall 3D structure of the scene.

Example:

```python
downsampled_cloud = point_cloud.voxel_down_sample(voxel_size=0.15)
```

A voxel size of `0.15` meters was used for the initial experiment.

This makes later processing faster and reduces unnecessary point density.

---

### 5. RANSAC Ground Plane Removal

The road surface usually forms the dominant flat plane in a driving scene. RANSAC-based plane segmentation is used to estimate this plane.

```python
plane_model, inliers = point_cloud.segment_plane(
    distance_threshold=0.2,
    ransac_n=3,
    num_iterations=1000
)
```

The detected plane is represented as:

```text
ax + by + cz + d = 0
```

Points close to this plane are treated as ground points. All other points are treated as non-ground points.

---

### 6. Ground and Non-Ground Separation

After detecting the ground plane, the point cloud is split into:

```text
Ground points = road surface
Non-ground points = vehicles, pedestrians, signs, poles, trees, and other objects
```

```python
ground_cloud = point_cloud.select_by_index(inliers)
non_ground_cloud = point_cloud.select_by_index(inliers, invert=True)
```

For visualization:

```text
Gray = ground points
Red = non-ground points
```

---

## Sample Result

Example command:

```bash
python main.py --bin_path data/velodyne/testing/velodyne/000010.bin
```

Sample output:

```text
Loading point cloud: data/velodyne/testing/velodyne/000010.bin
Raw points: 115875
Visualizing raw point cloud...
Points after ROI crop: 53552
Visualizing cropped point cloud...
Points after voxel downsampling: 17396
Visualizing downsampled point cloud...
Detected ground plane equation:
[-0.01004282  0.03282229  0.99941075  1.75464191]
Ground points: 7499
Non-ground points: 9897
Visualizing ground removal result...
```

The detected ground plane equation corresponds approximately to:

```text
-0.010x + 0.033y + 0.999z + 1.755 = 0
```

Since the z coefficient is close to `1.0`, the estimated plane is mostly horizontal, which is consistent with a road surface.

## Day 2: DBSCAN Clustering

After removing the ground plane, DBSCAN clustering was applied to the non-ground point cloud. The goal was to group nearby 3D points into object-like clusters that could represent vehicles, pedestrians, poles, signs, trees, or other scene structures.

DBSCAN was selected because it does not require a fixed number of clusters and can mark sparse points as noise. This makes it suitable for exploratory LiDAR point cloud clustering.

The main parameters were:

- `eps`: neighborhood radius in meters

- `min_points`: minimum number of nearby points needed to form a cluster

Several parameter settings were tested, including:

- `eps=0.5`, `min_points=10`

- `eps=0.8`, `min_points=10`

- `eps=1.0`, `min_points=10`

- `eps=0.8`, `min_points=20`

The best setting for the tested frame was selected based on visual inspection of whether object-like structures were separated cleanly without excessive fragmentation or merging.

The DBSCAN output provides object proposals that will be used in the next stage for 3D bounding box estimation.

---

## Repository Structure

```text
kitti-pointcloud-perception/
├── data/
│   └── velodyne/
├── results/
├── src/
│   ├── loader.py
│   ├── preprocess.py
│   └── visualize.py
├── main.py
├── requirements.txt
└── README.md
```

---

## File Descriptions

### `src/loader.py`

Handles loading KITTI `.bin` point cloud files.

Main responsibilities:

- Read raw binary LiDAR files
- Reshape data into `[x, y, z, intensity]`
- Separate XYZ coordinates and intensity values
- Convert NumPy arrays into Open3D point clouds

### `src/preprocess.py`

Contains preprocessing functions.

Main responsibilities:

- Crop the region of interest
- Apply voxel downsampling
- Remove the ground plane using RANSAC
- Separate ground and non-ground point clouds

### `src/visualize.py`

Contains Open3D visualization utilities.

Main responsibilities:

- Visualize raw point clouds
- Visualize cropped point clouds
- Visualize downsampled point clouds
- Visualize ground and non-ground points together

### `main.py`

Runs the complete Day 1 pipeline.

Main steps:

- Load KITTI point cloud
- Visualize raw point cloud
- Crop ROI
- Visualize cropped cloud
- Apply voxel downsampling
- Visualize downsampled cloud
- Remove ground plane
- Visualize ground removal result

---

## Current Status

Day 1 completed.

Completed components:

- KITTI `.bin` loading
- NumPy parsing
- Open3D point cloud conversion
- Raw point cloud visualization
- ROI cropping
- Voxel downsampling
- RANSAC ground plane removal
- Ground and non-ground point separation
- Ground removal visualization

---

## Next Steps

Planned next steps:

- Apply DBSCAN clustering on non-ground points
- Estimate 3D bounding boxes around clusters
- Filter clusters by size and point count
- Compute spatial metrics such as centroid and distance from ego vehicle
- Save object-level results to JSON
- Generate BEV visualizations
- Add screenshots to the README
- Polish the repository for portfolio presentation

---

## Skills Demonstrated

This Day 1 implementation demonstrates:

- 3D point cloud processing
- KITTI LiDAR data handling
- NumPy-based binary file parsing
- Open3D point cloud representation
- Region-of-interest filtering
- Voxel downsampling
- RANSAC plane segmentation
- Ground plane removal
- Basic autonomous perception pipeline design

---

## Limitations

The current version does not yet perform object detection or object clustering. It only prepares the point cloud by removing the ground plane and isolating non-ground points.

Future versions will add DBSCAN-based clustering, bounding box estimation, and spatial analysis to create a complete classical LiDAR perception pipeline.

---

## Planned Final Pipeline

```text
Raw KITTI LiDAR
        ↓
ROI Cropping
        ↓
Voxel Downsampling
        ↓
RANSAC Ground Removal
        ↓
DBSCAN Clustering
        ↓
Bounding Box Estimation
        ↓
Spatial Analysis
        ↓
BEV Visualization
```