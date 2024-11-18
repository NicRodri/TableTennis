import os
import json
import cv2
import shutil

# Paths
processed_data_folder = "processed_data"  # Path to processed data folder
images_folder = os.path.join(processed_data_folder, "images")  # Path to images folder
ball_markups_folder = os.path.join(processed_data_folder, "ball_markups")  # Path to ball markups folder
output_folder = "processed_data_yolo"  # Output folder for YOLO format

# Create YOLO folder structure
for split in ["train", "val"]:
    os.makedirs(os.path.join(output_folder, "images", split), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "labels", split), exist_ok=True)

# Function to convert bounding box to YOLO format
def convert_to_yolo_format(x, y, width, height, img_width, img_height):
    x_center = x / img_width
    y_center = y / img_height
    bbox_width = width / img_width
    bbox_height = height / img_height
    return f"0 {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}"  # Class 0 for "ball"

# Process each split
for split in ["train", "test"]:  # Rename 'test' to 'val' for YOLO format
    images_split_folder = os.path.join(images_folder, split)
    ball_markups_split_folder = os.path.join(ball_markups_folder, split)
    output_images_dir = os.path.join(output_folder, "images", "train" if split == "train" else "val")
    output_labels_dir = os.path.join(output_folder, "labels", "train" if split == "train" else "val")

    for game_folder in os.listdir(images_split_folder):
        game_image_path = os.path.join(images_split_folder, game_folder)
        ball_markup_path = os.path.join(ball_markups_split_folder, f"{game_folder}_ball_markup.json")

        if os.path.isdir(game_image_path) and os.path.exists(ball_markup_path):
            # Load ball markup JSON
            with open(ball_markup_path, "r") as file:
                ball_data = json.load(file)

            for image_file in sorted(os.listdir(game_image_path)):
                if image_file.endswith(".png") or image_file.endswith(".jpg"):
                    # Image path
                    image_path = os.path.join(game_image_path, image_file)

                    # Frame number (assumes sequential filenames like 0001.png)
                    frame_number = int(os.path.splitext(image_file)[0])

                    # Get ball position for the frame
                    ball_position = ball_data.get(str(frame_number), {"x": -1, "y": -1})
                    if ball_position["x"] == -1 or ball_position["y"] == -1:
                        # Skip frames where the ball is not visible
                        continue

                    # YOLO bounding box parameters
                    x = ball_position["x"]
                    y = ball_position["y"]
                    width = 20  # Approximate ball width in pixels
                    height = 20  # Approximate ball height in pixels

                    # Read image to get dimensions
                    img = cv2.imread(image_path)
                    img_height, img_width = img.shape[:2]

                    # Convert to YOLO format
                    yolo_bbox = convert_to_yolo_format(x, y, width, height, img_width, img_height)

                    # Prefix filenames with folder name
                    prefix = game_folder
                    prefixed_image_file = f"{prefix}_{image_file}"

                    # Save YOLO annotation
                    label_file = os.path.join(output_labels_dir, prefixed_image_file.replace(".png", ".txt").replace(".jpg", ".txt"))
                    with open(label_file, "w") as f:
                        f.write(yolo_bbox)

                    # Save image in YOLO structure with prefixed name
                    output_image_path = os.path.join(output_images_dir, prefixed_image_file)
                    shutil.copy(image_path, output_image_path)
