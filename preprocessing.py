import os
import json
import numpy as np
from tqdm import tqdm

# Paths
dataset_dir = "path/to/dataset"  # Replace with actual dataset path
output_dir = "processed_data"
os.makedirs(output_dir, exist_ok=True)

def preprocess_ball_annotations(markup_file, output_dir):
    with open(markup_file, 'r') as f:
        data = json.load(f)

    for frame, ball_data in tqdm(data.items()):
        x, y = ball_data.get('x', -1), ball_data.get('y', -1)
        if x != -1 and y != -1:  # Only process frames with valid ball data
            x_normalized = x / 1920
            y_normalized = y / 1080
            label_path = os.path.join(output_dir, f"{frame}.txt")
            with open(label_path, 'w') as lbl_file:
                lbl_file.write(f"0 {x_normalized} {y_normalized} 0.01 0.01\n")  # YOLO format

# Run preprocessing
markup_file = os.path.join(dataset_dir, "markup.json")  # Replace with correct path
preprocess_ball_annotations(markup_file, output_dir)
