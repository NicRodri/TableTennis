import os
import json

# Paths
data_folder = "data"  # Path to your dataset folder
output_folder = "processed_data"  # Path to save processed JSON files
os.makedirs(output_folder, exist_ok=True)

# Original and target resolutions
original_width, original_height = 1920, 1080
target_width, target_height = 640, 360

# Scaling factors
scale_x = target_width / original_width
scale_y = target_height / original_height

# Function to scale ball_markup.json
def process_ball_markup(input_path, output_path):
    with open(input_path, "r") as file:
        ball_data = json.load(file)

    # Scale coordinates
    for frame, coords in ball_data.items():
        if coords["x"] != -1 and coords["y"] != -1:  # Check for valid coordinates
            coords["x"] = int(coords["x"] * scale_x)
            coords["y"] = int(coords["y"] * scale_y)

    # Save the updated JSON file
    with open(output_path, "w") as file:
        json.dump(ball_data, file, indent=4)
    print(f"Processed ball_markup.json saved to: {output_path}")

# Process each game's JSON file
for folder in os.listdir(data_folder):
    folder_path = os.path.join(data_folder, folder)

    if os.path.isdir(folder_path):
        ball_markup_path = os.path.join(folder_path, "ball_markup.json")
        if os.path.exists(ball_markup_path):
            output_path = os.path.join(output_folder, f"{folder}_ball_markup.json")
            process_ball_markup(ball_markup_path, output_path)
