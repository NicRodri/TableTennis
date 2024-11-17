import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Constants
IMG_WIDTH = 1920
IMG_HEIGHT = 1080
TABLE_MIDPOINT = IMG_WIDTH // 2  # Midpoint of the table for detecting sides
BOUNCE_THRESHOLD = 5  # Minimum distance threshold to detect a valid bounce (pixels)

# Paths
processed_data_dir = "processed_data"
output_file = "scores.json"


def detect_bounce_side(x, table_midpoint):
    """Detect which side of the table the ball bounced on."""
    return "Player 1" if x < table_midpoint else "Player 2"


def score_tracking(rallies_file, trajectory_file):
    """Track scores based on rallies and ball trajectory."""
    with open(rallies_file, "r") as f:
        rallies = json.load(f)
    with open(trajectory_file, "r") as f:
        trajectory = json.load(f)

    player1_score = 0
    player2_score = 0
    scores = []

    for rally in rallies:
        rally_result = {"rally": rally, "winner": None}
        bounce_count = {"Player 1": 0, "Player 2": 0}
        fault = False

        for frame in rally:
            if str(frame) in trajectory:
                ball_event = trajectory[str(frame)]["event"]
                ball_x = trajectory[str(frame)]["x"]
                ball_y = trajectory[str(frame)]["y"]

                if ball_event == "bounce":
                    side = detect_bounce_side(ball_x, TABLE_MIDPOINT)
                    bounce_count[side] += 1

                if ball_event == "net":
                    fault = True
                    break

        if fault:
            # If a fault occurred, award the point to the other player
            if bounce_count["Player 1"] > 0:
                player2_score += 1
                rally_result["winner"] = "Player 2"
            else:
                player1_score += 1
                rally_result["winner"] = "Player 1"
        else:
            # Check bounce rules to determine the winner
            if bounce_count["Player 1"] > 1:
                player2_score += 1
                rally_result["winner"] = "Player 2"
            elif bounce_count["Player 2"] > 1:
                player1_score += 1
                rally_result["winner"] = "Player 1"

        scores.append(rally_result)

    # Final Scores
    final_scores = {
        "Player 1": player1_score,
        "Player 2": player2_score,
        "rallies": scores,
    }

    # Save results
    with open(output_file, "w") as f:
        json.dump(final_scores, f, indent=4)

    return final_scores


def visualize_all_rallies(trajectory_file, all_rallies, table_mask, net_mask, table_width=1920, table_height=1080):
    """Visualize the trajectory for all rallies with scaled masks."""
    with open(trajectory_file, "r") as f:
        trajectory = json.load(f)


    plt.figure(figsize=(15, 8))
    plt.imshow(table_mask, cmap="Reds", alpha=0.3, extent=[0, table_width, 0, table_height])
    plt.imshow(net_mask, cmap="Blues", alpha=0.3, extent=[0, table_width, 0, table_height])
    plt.axvline(x=table_width / 2, color="blue", linestyle="--", label="Net")

    for rally_index, rally_frames in enumerate(all_rallies):
        for frame in rally_frames:
            if str(frame) in trajectory:
                x = trajectory[str(frame)]["x"]
                y = trajectory[str(frame)]["y"]
                plt.scatter(x, y, label=f"Rally {rally_index + 1}, Frame {frame}" if frame == rally_frames[0] else "")

    plt.xlim(0, table_width)
    plt.ylim(0, table_height)
    plt.title("Ball Trajectories for All Rallies")
    plt.xlabel("X Coordinate (pixels)")
    plt.ylabel("Y Coordinate (pixels)")
    plt.legend(loc="upper right", fontsize="small", bbox_to_anchor=(1.1, 1.05))
    plt.show()



def process_game_folder(folder_path):
    """Process a single game folder to track scores and visualize rallies."""
    rallies_file = os.path.join(folder_path, "rallies.json")
    trajectory_file = os.path.join(folder_path, "ball_trajectory_with_events.json")
    table_mask_template = os.path.join(folder_path, "{}_table.npy")
    net_mask_template = os.path.join(folder_path, "{}_net.npy")

    if os.path.exists(rallies_file) and os.path.exists(trajectory_file):
        # Track scores
        scores = score_tracking(rallies_file, trajectory_file)
        print("Final Scores:", scores)

        # Visualize all rallies
        if scores["rallies"]:
            # Collect all rally frames
            all_rallies_frames = [rally["rally"] for rally in scores["rallies"]]

            # Load masks dynamically based on the first frame of the first rally
            first_frame = all_rallies_frames[0][0]
            table_mask_path = table_mask_template.format(first_frame)
            net_mask_path = net_mask_template.format(first_frame)

            if os.path.exists(table_mask_path) and os.path.exists(net_mask_path):
                table_mask = np.load(table_mask_path)
                net_mask = np.load(net_mask_path)

                visualize_all_rallies(trajectory_file, all_rallies_frames, table_mask, net_mask)
            else:
                print(f"Missing table or net mask for frame {first_frame}. Skipping visualization.")

# Process all game folders
for folder in os.listdir(processed_data_dir):
    folder_path = os.path.join(processed_data_dir, folder)
    if os.path.isdir(folder_path):
        print(f"Processing folder: {folder}")
        process_game_folder(folder_path)

