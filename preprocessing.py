import os
import json
import numpy as np
from PIL import Image
from tqdm import tqdm
from scipy.interpolate import interp1d

# Paths
dataset_dir = "data"  # Replace with your dataset folder path
output_root = "processed_data"
os.makedirs(output_root, exist_ok=True)

# Table dimensions (example values, adjust as necessary)
IMG_WIDTH = 1920
IMG_HEIGHT = 1080
TABLE_MIDPOINT = IMG_WIDTH // 2  # Divide table into left/right sides


def preprocess_ball_annotations(markup_file, output_dir, img_width=IMG_WIDTH, img_height=IMG_HEIGHT):
    """Preprocess ball_markup.json into YOLO format."""
    with open(markup_file, 'r') as f:
        data = json.load(f)

    for frame, ball_data in tqdm(data.items(), desc=f"Processing {markup_file}"):
        x, y = ball_data.get("x", -1), ball_data.get("y", -1)
        if x != -1 and y != -1:  # Only process frames with valid ball data
            x_normalized = x / img_width
            y_normalized = y / img_height
            label_path = os.path.join(output_dir, f"{frame}_ball.txt")
            with open(label_path, "w") as lbl_file:
                lbl_file.write(f"0 {x_normalized} {y_normalized} 0.01 0.01\n")  # YOLO format


def preprocess_event_annotations(event_file, output_dir):
    """Preprocess events_markup.json into event labels."""
    with open(event_file, "r") as f:
        data = json.load(f)

    for frame, event in tqdm(data.items(), desc=f"Processing {event_file}"):
        label_path = os.path.join(output_dir, f"{frame}_event.txt")
        with open(label_path, "w") as lbl_file:
            if event == "bounce":
                lbl_file.write("1\n")  # Label for bounce
            elif event == "net":
                lbl_file.write("2\n")  # Label for net
            elif event == "empty_event":
                lbl_file.write("0\n")  # Label for empty event


def preprocess_segmentation_masks(mask_folder, output_dir):
    """Extract table, net, and player regions from segmentation masks."""
    for mask_file in tqdm(os.listdir(mask_folder), desc=f"Processing {mask_folder}"):
        frame_number = mask_file.split(".")[0]
        mask_path = os.path.join(mask_folder, mask_file)
        mask = np.array(Image.open(mask_path))

        # Extract table (red), net (blue), and players (green)
        table_mask = (mask[:, :, 0] > 0) & (mask[:, :, 1] == 0) & (mask[:, :, 2] == 0)  # Red region
        net_mask = (mask[:, :, 2] > 0) & (mask[:, :, 0] == 0) & (mask[:, :, 1] == 0)  # Blue region
        player_mask = (mask[:, :, 1] > 0) & (mask[:, :, 0] == 0) & (mask[:, :, 2] == 0)  # Green region

        # Ensure boolean masks are converted to uint8 for saving
        table_mask = table_mask.astype(np.uint8)
        net_mask = net_mask.astype(np.uint8)
        player_mask = player_mask.astype(np.uint8)

        # Save extracted masks as .npy files
        np.save(os.path.join(output_dir, f"{frame_number}_table.npy"), table_mask)
        np.save(os.path.join(output_dir, f"{frame_number}_net.npy"), net_mask)
        np.save(os.path.join(output_dir, f"{frame_number}_player.npy"), player_mask)


def generate_ball_trajectory_with_events(markup_file, event_file, output_file):
    """Generate ball trajectory from markup file with events included."""
    with open(markup_file, "r") as f:
        ball_data = json.load(f)
    with open(event_file, "r") as f:
        events = json.load(f)

    frames = []
    positions = []
    events_data = {}

    for frame, coords in ball_data.items():
        x, y = coords.get("x", -1), coords.get("y", -1)
        if x != -1 and y != -1:
            frames.append(int(frame))
            positions.append((x, y))
            events_data[int(frame)] = events.get(frame, "empty_event")

    # Interpolate missing frames
    frames = np.array(frames)
    positions = np.array(positions)
    interp_x = interp1d(frames, positions[:, 0], kind="linear", fill_value="extrapolate")
    interp_y = interp1d(frames, positions[:, 1], kind="linear", fill_value="extrapolate")

    # Generate trajectory for all frames
    all_frames = np.arange(min(frames), max(frames) + 1)
    trajectory = {
        int(frame): {
            "x": float(interp_x(frame)),
            "y": float(interp_y(frame)),
            "event": events_data.get(int(frame), "empty_event"),
        }
        for frame in all_frames
    }

    # Save to output file
    with open(output_file, "w") as out_f:
        json.dump(trajectory, out_f)


def segment_rallies(event_file):
    """Segment the game into rallies based on events."""
    with open(event_file, "r") as f:
        events = json.load(f)

    rallies = []
    current_rally = []

    for frame, event in sorted(events.items(), key=lambda x: int(x[0])):
        if event == "bounce":
            if not current_rally:
                current_rally = [frame]  # Start of rally
        elif event in {"net", "empty_event"}:
            if current_rally:
                current_rally.append(frame)  # End of rally
                rallies.append(current_rally)
                current_rally = []

    return rallies


def process_all_folders(dataset_dir, output_root):
    """Process all game/test folders in the dataset directory."""
    for folder in os.listdir(dataset_dir):
        folder_path = os.path.join(dataset_dir, folder)
        if os.path.isdir(folder_path):
            # Paths for markup files and segmentation masks
            ball_markup_file = os.path.join(folder_path, "ball_markup.json")
            event_markup_file = os.path.join(folder_path, "events_markup.json")
            mask_folder = os.path.join(folder_path, "segmentation_masks")
            output_dir = os.path.join(output_root, folder)
            os.makedirs(output_dir, exist_ok=True)

            # Process ball_markup.json if it exists
            if os.path.exists(ball_markup_file) and os.path.exists(event_markup_file):
                print(f"Processing ball markup and events in folder: {folder}")
                preprocess_ball_annotations(ball_markup_file, output_dir)

                # Generate ball trajectory with events
                trajectory_file = os.path.join(output_dir, "ball_trajectory_with_events.json")
                generate_ball_trajectory_with_events(ball_markup_file, event_markup_file, trajectory_file)

            # Process events_markup.json if it exists
            if os.path.exists(event_markup_file):
                print(f"Processing event markup in folder: {folder}")
                preprocess_event_annotations(event_markup_file, output_dir)

                # Segment rallies
                rallies = segment_rallies(event_markup_file)
                with open(os.path.join(output_dir, "rallies.json"), "w") as f:
                    json.dump(rallies, f)

            # Process segmentation masks if folder exists
            if os.path.exists(mask_folder):
                print(f"Processing segmentation masks in folder: {folder}")
                preprocess_segmentation_masks(mask_folder, output_dir)


# Run preprocessing for all folders
process_all_folders(dataset_dir, output_root)
