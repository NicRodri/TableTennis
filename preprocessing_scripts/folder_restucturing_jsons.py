import os
import shutil

# Paths
data_folder = "data"  # Original data folder containing events_markup.json
processed_data_folder = "processed_data"  # Destination folder for processed data
output_events_folder = os.path.join(processed_data_folder, "events")  # Destination for events JSONs

# Create the output directory structure
os.makedirs(os.path.join(output_events_folder, "train"), exist_ok=True)
os.makedirs(os.path.join(output_events_folder, "test"), exist_ok=True)

# Process each folder in the original data folder
for folder in os.listdir(data_folder):
    folder_path = os.path.join(data_folder, folder)
    
    if os.path.isdir(folder_path):
        # Determine if this is for training or testing
        is_train = folder.startswith("game")
        output_split_dir = os.path.join(output_events_folder, "train" if is_train else "test")
        
        # Path to the events_markup.json file
        events_file_path = os.path.join(folder_path, "events_markup.json")
        
        if os.path.exists(events_file_path):
            # Destination path for the events_markup.json file
            output_events_file = os.path.join(output_split_dir, f"{folder}_events_markup.json")
            
            # Copy the file
            shutil.copy(events_file_path, output_events_file)
            print(f"Copied: {events_file_path} -> {output_events_file}")
        else:
            print(f"No events_markup.json found in: {folder_path}")

# Paths
processed_data_folder = "processed_data"  # Base processed_data folder
ball_markups_folder = processed_data_folder  # Current location of ball_markups
output_ball_markups_folder = os.path.join(processed_data_folder, "ball_markups")  # Destination folder

# Create output directory structure
os.makedirs(os.path.join(output_ball_markups_folder, "train"), exist_ok=True)
os.makedirs(os.path.join(output_ball_markups_folder, "test"), exist_ok=True)

# Move and rename ball_markup.json files
for file in os.listdir(ball_markups_folder):
    if file.endswith("_ball_markup.json"):
        # Determine if the file belongs to train or test
        is_train = file.startswith("game")
        split_folder = "train" if is_train else "test"
        
        # Construct source and destination paths
        source_path = os.path.join(ball_markups_folder, file)
        destination_path = os.path.join(output_ball_markups_folder, split_folder, file)
        
        # Move the file
        shutil.move(source_path, destination_path)
        print(f"Moved: {source_path} -> {destination_path}")