import json, csv

def make_json_safe_detection(detection):
    safe_detection = {}

    for key, value in detection.items():
        if key == 'bbox': continue
        safe_detection[key] = value

    return safe_detection

def save_detections_json(detections, output_path):
    safe_detections = [make_json_safe_detection(detection) for detection in detections]

    with open(output_path, "w") as f:
        json.dump(safe_detections, f, indent=4)
    
    print(f"Saved detection JSON to {output_path}")

def save_detections_csv(detections, output_path):
    safe_detections = [make_json_safe_detection(detection) for detection in detections]

    if len(safe_detections) == 0:
        print("No detections to save as CSV")
        return
    
    fieldnames = [
        "frame_id",
        "cluster_id",
        "class_heuristic",
        "num_points",
        "center_x",
        "center_y",
        "center_z",
        "extent_x",
        "extent_y",
        "extent_z",
        "volume",
        "density",
        "distance_3d_m",
        "distance_xy_m",
        "relative_position"
    ]

    rows = []

    for detection in safe_detections:
        center = detection["center"]
        extent = detection["extent"]

        rows.append({
            "frame_id": detection.get("frame_id"),
            "cluster_id": detection.get("cluster_id"),
            "class_heuristic": detection.get("class_heuristic"),
            "num_points": detection.get("num_points"),
            "center_x": center[0],
            "center_y": center[1],
            "center_z": center[2],
            "extent_x": extent[0],
            "extent_y": extent[1],
            "extent_z": extent[2],
            "volume": detection.get("volume"),
            "density": detection.get("density"),
            "distance_3d_m": detection.get("distance_3d_m"),
            "distance_xy_m": detection.get("distance_xy_m"),
            "relative_position": detection.get("relative_position"),
        })
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved detection CSV to {output_path}")