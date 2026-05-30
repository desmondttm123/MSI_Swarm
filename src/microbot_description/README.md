# microbot_description

ROS 2 Jazzy URDF/Xacro, RViz, Gazebo Sim, ros2_control, joystick teleop, SLAM Toolbox, and Nav2 bringup for the MicroBot.

## Location

This package is in the right place for a colcon workspace:

```bash
/home/msi/swarm_ws/src/microbot_description
```

## Build and source

```bash
cd /home/msi/swarm_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select microbot_description
source install/setup.bash
```

## View in RViz only

This uses `robot_state_publisher` plus `joint_state_publisher` so RViz receives joint states for the continuous wheel joints.

```bash
ros2 launch microbot_description description.launch.py
```

If you only want TF/robot_description without joint state publishing:

```bash
ros2 launch microbot_description description.launch.py use_joint_state_publisher:=false
```

## Gazebo simulation with ros2_control

```bash
ros2 launch microbot_description sim.launch.py
```

Joystick teleop starts with the sim by default. Disable it with:

```bash
ros2 launch microbot_description sim.launch.py use_joy:=false
```

This starts Gazebo Sim, spawns the robot, bridges `/scan`, `/imu`, `/odom`, `/tf`, `/clock`, and `/diff_drive_controller/cmd_vel_unstamped`, and opens RViz. The default motion path uses Gazebo Sim's native DiffDrive plugin so teleop works reliably on Jazzy. The ros2_control tags/config remain in the package, but controller loading is not enabled by default because this system currently hits a Jazzy `gz_ros2_control` argument parsing issue.

Headless/no-RViz test mode:

```bash
ros2 launch microbot_description sim.launch.py gui:=false use_rviz:=false
```

## Drive it

Keyboard:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
```

Joystick:

```bash
ros2 launch microbot_description teleop_joy.launch.py
```

Default joystick mapping is left stick vertical for forward/back, left stick horizontal for yaw, LB to enable, RB for turbo. Edit `config/joy.yaml` if your controller maps axes differently.

## SLAM

Start the sim first, then in another terminal:

```bash
cd /home/msi/swarm_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch microbot_description slam.launch.py
```

## Nav2 with SLAM

With sim and SLAM already running, start Nav2:

```bash
ros2 launch microbot_description nav2.launch.py
```

`nav2.launch.py` uses `config/nav2_params.yaml` and remaps Nav2 `/cmd_vel` to `/diff_drive_controller/cmd_vel_unstamped`.

## Notes

- The URDF dimensions are based on the firmware values in `MicroBotControl_Lidar/MicroBotControl_Lidar.ino`.
- The Gazebo inertias, chassis size, wheel width, and sensor mount positions are reasonable placeholders. Measure the real robot and tune the xacro when you can.
- The LiDAR mount yaw is set to the firmware-derived right-facing orientation. If scans look rotated in RViz, adjust `lidar_mount_yaw_deg` in `urdf/microbot.urdf.xacro`.
