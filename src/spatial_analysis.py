import math

def computer_distance_metrics(center):
    x = float(center[0])
    y = float(center[1])
    z = float(center[2])

    distance_3d = math.sqrt(x**2 + y**2 + z**2)
    distance_xy = math.sqrt(x**2 + y**2)

    return {
        "distance_3d_m": round(distance_3d, 2),
        "distance_xy_m": round(distance_xy, 2)
    }

def assign_relative_position(center):
    x = float(center[0])
    y = float(center[1])

    if x < 0: return "behind_ego"
    if x < 5: distance_zone = "near_front"
    elif x < 20: distance_zone = "mid_front"
    else: distance_zone = "far_front"

    if y > 2: side = "left"
    elif y < -2: side = "right"
    else: side = "center"

    return f"{distance_zone}_{side}"

def add_spatial_analysis(detections):
    enriched_detections = []

    for detection in detections:
        center = detection["center"]

        distance_metrics = computer_distance_metrics(center)
        relative_position = assign_relative_position(center)

        detection_with_spatial = detection.copy()
        detection_with_spatial.update(distance_metrics)
        detection_with_spatial["relative_position"] = relative_position

        enriched_detections.append(detection_with_spatial)

    return enriched_detections