# PX4/Gazebo Camera Python Setup Guide

This is a guide to get camera data from PX4 gazebo without the ros bridge, using Gstreamer and Gazebo transport. You can then write the data to an udp port to use later or just use it

---
## Step 0: PX4 setup
   If you do not have PX4 simulation follow this https://docs.px4.io/main/en/dev_setup/dev_env_linux_ubuntu.html#simulation-and-nuttx-pixhawk-targets
## Step 1: Create a Python Virtual Environment

1. Create the directory you will use:

   ```bash
   mkdir <your_project_directory>
   cd <your_project_directory>
   ```
2. Create a virtual environment with access to system site packages (required to use `gz` globally):

   ```bash
   python3 -m venv --system-site-packages .venv
   ```
3. Optionally, Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

---

## Step 2: Install Gazebo-Python Bridges

1. Exit the virtual environment:

   ```bash
   deactivate
   ```

2. Install the required system packages (version should match your Gazebo version or use the latest available):

   ```bash
   sudo apt install python3-gz-transport13
   sudo apt install python3-gz-msgs10
   ```

   > `python3-gz-msgs10` allows you to import Gazebo topics. Skip if already installed.

3. Enter the virtual environment and test the import:

   ```bash
   source .venv/bin/activate
   python3 -c "import gz.transport13 as gz; print('OK')"
   ```

---

## Step 3: Install GStreamer and Build OpenCV with GStreamer
This part is acquired from https://discuss.bluerobotics.com/t/opencv-python-with-gstreamer-backend/8842
1. If you already have OpenCV installed in the virtual environment, remove it:

   ```bash
   pip uninstall opencv-python opencv-contrib-python
   ```

2. Install GStreamer globally:

   ```bash
   sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
   libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
   gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools \
   gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 \
   gstreamer1.0-qt5 gstreamer1.0-pulseaudio
   ```
2,5. In case you do not have GUI interfaces needed to show images in opencv, do 

   ```bash
   sudo apt update
   sudo apt install -y libgtk2.0-dev pkg-config
   ```

3. Build OpenCV with GStreamer support in the virtual environment:

   ```bash
   # Navigate to a folder where you want the OpenCV repo
   git clone --recursive https://github.com/skvark/opencv-python.git
   cd opencv-python

   # Enable GStreamer
   export CMAKE_ARGS="-DWITH_GSTREAMER=ON -DWITH_GTK=ON"

   # Upgrade pip and wheel
   pip install --upgrade pip wheel

   # Build the wheel (can take from 5 minutes to >2 hours depending on hardware)
   pip wheel . --verbose

   # Install the generated wheel (usually in the dist/ folder)
   pip install dist/opencv_python*.whl
   ```

---

## Step 4: Build Mono Camera PX4 SITL

1. Navigate to your autopilot folder and build the PX4 SITL with the mono camera:

   ```bash
   make px4_sitl gz_x500_mono_cam
   ```

2. Verify if the camera topic is being published:

   ```bash
   gz topic -i -t /camera
   ```

3. Optionally, list all topics:

   ```bash
   gz topic --list
   ```
   
NOTE:
/camera is nonexistant in some later versions of the autopilot instead to the step 3 and locate the topic with /image, it could be something like 
/world/default/model/x500_mono_cam_down_0/link/camera_link/sensor/imager/image

---

## Python Code explanation
1. Import the transport
   ```bash
   import gz.transport13 as gz 
   import gz.msgs10.image_pb2 as msgs
   ```
2. create the subscriber
      ```bash
   self.node = gz.Node()
   self.sub = self.node.subscribe(msgs.Image, "/camera", self.image_callback) #image_callback is the function that will be run after the video is captured in gazebo
   ```
You can initialize the writer with gstreamer to the port you want to stream to, and then write the stream from subscriber as the class VideoUDPWriter does
