def classify_cluster_by_size(extent):
    length = float(extent[0])
    width = float(extent[1])
    height = float(extent[2])

    dims_sorted = sorted([length, width, height], reverse=True)
    longest = dims_sorted[0]
    middle = dims_sorted[1]

    if 2.0 <= longest <= 7.0 and 1.0 <= middle <= 3.0 and 1.0 <= height <= 3.0:
        return "vehicle_like"
    
    if 0.2 <= longest <= 2.0 and 0.2 <= middle <= 1.5 and 0.8 <= height <= 2.5:
        return "pedestrian_or_pole_like"

    return "unknown"

def create_bounding_box_detections(clusters):
    detections = []
    geometries = []

    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        num_points = cluster["num_points"]
        cluster_cloud = cluster["cluster_cloud"]

        if len(cluster_cloud.points) == 0: continue
        bbox = cluster_cloud.get_axis_aligned_bounding_box()

        center =  bbox.get_center()
        extent =  bbox.get_extent()

        length = float(extent[0])
        width = float(extent[1])
        height = float(extent[2])

        volume = float(extent[0] * extent[1] * extent[2])
        density = float(num_points / volume) if volume > 0 else 0.0

        center_x = float(center[0])
        center_y = float(center[1])
        center_z = float(center[2])

        print(
            f"Cluster {cluster_id}: "
            f"points={num_points}, "
            f"center=[{center_x:.2f}, {center_y:.2f}, {center_z:.2f}], "
            f"extent=[{length:.2f}, {width:.2f}, {height:.2f}], "
            f"density={density:.2f}"
        )

        if center_x < 2.5: 
            print(f"Rejected cluster {cluster_id}: too close to ego vehicle")
            continue

        if length > 8.0 or width > 4.0 or height > 3.5: continue
        if height < 0.3: continue
        if length < 0.2 or width < 0.2: continue
        if density < 1.0: continue

        bbox.color = (0, 1, 0)

        class_heuristic = classify_cluster_by_size(extent)

        detection = {
            "cluster_id": int(cluster_id),
            "num_points": int(num_points),
            "center": [round(float(v), 2) for v in center],
            "extent": [round(float(v), 2) for v in extent],
            "volume": round(float(volume), 2),
            "density": round(float(density), 2),
            "class_heuristic": class_heuristic,
            "bbox": bbox,
        }

        detections.append(detection)
        geometries.append(cluster_cloud)
        geometries.append(bbox)

    return detections, geometries

def print_detection_summary(detections, max_items=20):
    print("\n3D Bounding Box Detection Summary")
    print("--------------------------------")

    if len(detections) == 0:
        print("No valid detections found.")
        return
    
    for det in detections[:max_items]:
        center = det["center"]
        extent = det["extent"]
        print(
            f"Cluster {det['cluster_id']} | "
            f"{det['class_heuristic']} | "
            f"points={det['num_points']} | "
            f"center=[{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}] | "
            f"extent=[{extent[0]:.2f}, {extent[1]:.2f}, {extent[2]:.2f}] | "
            f"density={det['density']:.2f}"
        )