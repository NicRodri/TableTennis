import numpy as np
import matplotlib.pyplot as plt

# Load masks
table_mask = np.load("processed_data/game_1/14_table.npy")
net_mask = np.load("processed_data/game_1/14_net.npy")
player_mask = np.load("processed_data/game_1/14_player.npy")

# Visualize masks
plt.imshow(table_mask, cmap="Reds")
plt.title("Table Mask")
plt.show()

plt.imshow(net_mask, cmap="Blues")
plt.title("Net Mask")
plt.show()

plt.imshow(player_mask, cmap="Greens")
plt.title("Player Mask")
plt.show()
