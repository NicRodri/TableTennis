import os
import shutil
import random

# Paths
processed_data_folder = "processed_data_yolo"  # Current folder structure
output_folder = "dataset_yolo"  # Target folder structure

# Create target folder structure
for split in ["train", "val", "test"]:
    os.makedirs(os.path.join(output_folder, "images", split), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "labels", split), exist_ok=True)

# Split ratio
split_ratio = 0.2  # 20% for validation

# Paths for train, val (now containing test), and test
current_train_images_path = os.path.join(processed_data_folder, "images", "train")
current_train_labels_path = os.path.join(processed_data_folder, "labels", "train")
current_val_images_path = os.path.join(processed_data_folder, "images", "val")  # This folder contains test data
current_val_labels_path = os.path.join(processed_data_folder, "labels", "val")  # This folder contains test labels

# Target paths
train_images_path = os.path.join(output_folder, "images", "train")
val_images_path = os.path.join(output_folder, "images", "val")
test_images_path = os.path.join(output_folder, "images", "test")
train_labels_path = os.path.join(output_folder, "labels", "train")
val_labels_path = os.path.join(output_folder, "labels", "val")
test_labels_path = os.path.join(output_folder, "labels", "test")

# Step 1: Move test data from current val to new test
test_image_files = sorted([f for f in os.listdir(current_val_images_path) if f.startswith("test_") and (f.endswith(".png") or f.endswith(".jpg"))])

for file in test_image_files:
    shutil.move(os.path.join(current_val_images_path, file), os.path.join(test_images_path, file))
    label_file = file.replace(".png", ".txt").replace(".jpg", ".txt")
    shutil.move(os.path.join(current_val_labels_path, label_file), os.path.join(test_labels_path, label_file))

# Step 2: Handle remaining train/val split
remaining_image_files = sorted([f for f in os.listdir(current_train_images_path) if f.endswith(".png") or f.endswith(".jpg")])
random.shuffle(remaining_image_files)

# Split into train and val
split_index = int(len(remaining_image_files) * (1 - split_ratio))
train_files = remaining_image_files[:split_index]
val_files = remaining_image_files[split_index:]

# # Move train files
# for file in train_files:
#     shutil.move(os.path.join(current_train_images_path, file), os.path.join(train_images_path, file))
#     label_file = file.replace(".png", ".txt").replace(".jpg", ".txt")
#     shutil.move(os.path.join(current_train_labels_path, label_file), os.path.join(train_labels_path, label_file))

# Move val files
for file in val_files:
    shutil.move(os.path.join(current_train_images_path, file), os.path.join(val_images_path, file))
    label_file = file.replace(".png", ".txt").replace(".jpg", ".txt")
    shutil.move(os.path.join(current_train_labels_path, label_file), os.path.join(val_labels_path, label_file))

print("Dataset successfully split into train, val, and test!")
