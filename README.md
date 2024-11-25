# Install guide no CPU:

# Go to the microsoft store and install ubuntu 18.04.06 LTS

# Open wsl using this version once its installed. You can do that by searching ubuntu and selecting the version on the windows search.

# Run the following commands:

sudo apt update
sudo apt upgrade
sudo apt install libopencv-dev python3-opencv
sudo apt install cmake

git clone https://github.com/AlexeyAB/darknet
cd darknet

sudo vim Makefile

# In the file make sure to set OPENCV to 1 as seen below

OPENCV=1

# once done save and then run make with the command below:

make


# Once done make sure you move the ball_v1* (aka .weights, .data, .cfg, .names) and video file (aka test video to track scoring) to the darknet directory. The video can be found on the nextcloud, and the ball_v1* can be found in our repo. Jeffs version is in main and Nico's version is in small_imgs branch.

# The repo can be found here: https://github.com/NicRodri/TableTennis

# Then go to ball_v1.data and change the names to the directory your darknet folder is in as seen below:

names = /root/scarlet/darknet/ball_v1.names

# Do not worry about the other folders, they do not matter.


# Once you finish that run the following to test the video:

./darknet detector demo ball_v1.data ball_v1.cfg ball_v1_best.weights -ext_output WIN_20241124_11_54_55_Pro.mp4

# Note the training video here was used for reference, any video can be used. The video is available on nextcloud and found in our discord chat.