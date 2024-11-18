import os
import cv2

# Paths
data_folder = "data"  # Path to your dataset folder
output_folder = "processed_data"  # Path to save processed masks
target_resolution = (640, 360)  # Target resolution (width, height)

# Create output directories for masks
os.makedirs(os.path.join(output_folder, "masks/train"), exist_ok=True)
os.makedirs(os.path.join(output_folder, "masks/test"), exist_ok=True)

# Process each folder
for folder in os.listdir(data_folder):
    folder_path = os.path.join(data_folder, folder)
    if os.path.isdir(folder_path):
        # Determine if this is for training or testing
        is_train = folder.startswith("game")
        output_masks_dir = os.path.join(output_folder, "masks/train" if is_train else "masks/test")

        # Prepare folder for current game/test
        output_game_folder = os.path.join(output_masks_dir, folder)
        os.makedirs(output_game_folder, exist_ok=True)

        # Process segmentation masks
        masks_folder = os.path.join(folder_path, "segmentation_masks")
        if os.path.exists(masks_folder):
            # Sort mask files numerically (accounting for inconsistent naming)
            mask_files = sorted(os.listdir(masks_folder), key=lambda x: int(os.path.splitext(x)[0]))

            for i, mask_file in enumerate(mask_files):
                if mask_file.endswith(".png"):
                    mask_path = os.path.join(masks_folder, mask_file)
                    mask = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)

                    # Resize the mask
                    resized_mask = cv2.resize(mask, target_resolution, interpolation=cv2.INTER_NEAREST)

                    # Rename the mask to follow 0001.png format
                    new_mask_name = f"{i+1:04d}.png"  # Sequential naming with 4-digit padding
                    output_mask_path = os.path.join(output_game_folder, new_mask_name)

                    # Save the resized mask
                    cv2.imwrite(output_mask_path, resized_mask)

                    # Debug output to verify the process
                    print(f"Processed mask saved to: {output_mask_path}")
