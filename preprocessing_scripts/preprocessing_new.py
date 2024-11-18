import os
import cv2
import subprocess

# Paths
data_folder = "data"  # Path to your dataset folder
output_folder = "processed_data"  # Path to save processed files
target_resolution = (640, 360)  # Target resolution (width, height)

# Create output directories
os.makedirs(os.path.join(output_folder, "images/train"), exist_ok=True)
os.makedirs(os.path.join(output_folder, "masks/train"), exist_ok=True)
os.makedirs(os.path.join(output_folder, "images/test"), exist_ok=True)
os.makedirs(os.path.join(output_folder, "masks/test"), exist_ok=True)

# FFmpeg CUDA command template
ffmpeg_command_template = (
    "ffmpeg -y -hwaccel cuda -i {input_video} -vf scale={width}:{height} "
    "{output_images}/%04d.png"
)

# Process each folder
for folder in os.listdir(data_folder):
    folder_path = os.path.join(data_folder, folder)
    if os.path.isdir(folder_path):
        # Determine if this is for training or testing
        is_train = folder.startswith("game")
        output_images_dir = os.path.join(output_folder, "images/train" if is_train else "images/test")
        output_masks_dir = os.path.join(output_folder, "masks/train" if is_train else "masks/test")

        # Process videos using FFmpeg
        for file in os.listdir(folder_path):
            if file.endswith(".mp4"):  # Check for video files
                video_path = os.path.join(folder_path, file)

                # Prepare output directory for extracted frames
                video_output_images_dir = os.path.join(output_images_dir, folder)
                os.makedirs(video_output_images_dir, exist_ok=True)

                # Build FFmpeg command
                ffmpeg_command = ffmpeg_command_template.format(
                    input_video=video_path,
                    width=target_resolution[0],
                    height=target_resolution[1],
                    output_images=video_output_images_dir
                )

                # Execute FFmpeg command
                subprocess.run(ffmpeg_command, shell=True, check=True)

        # Process segmentation masks
        masks_folder = os.path.join(folder_path, "segmentation_masks")
        if os.path.exists(masks_folder):
            for mask_file in os.listdir(masks_folder):
                if mask_file.endswith(".png"):
                    mask_path = os.path.join(masks_folder, mask_file)
                    mask = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)

                    # Resize mask
                    resized_mask = cv2.resize(mask, target_resolution, interpolation=cv2.INTER_NEAREST)

                    # Save mask with corresponding filename
                    mask_filename = f"{folder}_{mask_file}"  # Prefix mask filenames with folder name
                    cv2.imwrite(os.path.join(output_masks_dir, mask_filename), resized_mask)
