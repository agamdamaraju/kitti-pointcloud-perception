import json, matplotlib.pyplot as plt, matplotlib.patches as patches

def plot_dev_detections(detections, output_path, x_limit=(0, 30), y_limit=(-15, 15)):
    fig, ax = plt.subplots(figsize=(8,8))

    ax.scatter(0, 0, marker="x", s=100, label="Ego vehicle")

    for detection in detections:
        center = detection["center"]
        extent = detection["extent"]

        center_x = float(center[0])
        center_y = float(center[1])

        length = float(extent[0])
        width = float(extent[1])

        class_label = detection.get("class_heuristic", "object")
        relative_position = detection.get("relative_position", "")

        bottom_left_x = center_x - length / 2
        bottom_left_y = center_y - width / 2

        rect = patches.Rectangle(
            (bottom_left_x, bottom_left_y),
            length,
            width,
            fill=False,
            linewidth=2,
            label=class_label
        )

        ax.add_patch(rect)
        ax.scatter(center_x, center_y, s=40)

        label_text = f"{class_label}\n{relative_position}"
        ax.text(
            center_x,
            center_y + width / 2 + 0.4,
            label_text,
            fontsize=8,
            ha="center",
            va="bottom"
        )
    
    ax.set_xlim(x_limit)
    ax.set_ylim(y_limit)

    ax.set_xlabel("Forward distance x (m)")
    ax.set_ylabel("Left/right distance y (m)")
    ax.set_title("Bird's-Eye-View Object Proposal Visualization")
    ax.grid(True)
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved BEV visualization to {output_path}")