import os
import subprocess

# Base directory containing the test folders
base_dir = r"F:\BCIT\TERM 4\AI Project\TableTennis\processed_data\images\test"
output_dir = r"F:\BCIT\TERM 4\AI Project\TableTennis\processed_data\videos\test"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Frame rate for the videos
frame_rate = 30

# Iterate through each folder in the base directory
for folder_name in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder_name)
    if os.path.isdir(folder_path):
        # Define the output video path
        output_video_path = os.path.join(output_dir, f"{folder_name}.mp4")
        
        # FFmpeg command to create a video from the images in the folder
        ffmpeg_command = [
            "ffmpeg",
            "-framerate", str(frame_rate),
            "-i", os.path.join(folder_path, "%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_video_path
        ]
        
        # Run the command
        try:
            subprocess.run(ffmpeg_command, check=True)
            print(f"Video created: {output_video_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating video for folder {folder_name}: {e}")
