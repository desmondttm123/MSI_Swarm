from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare("microbot_description")
    ros_gz_sim_share = FindPackageShare("ros_gz_sim")

    xacro_file = PathJoinSubstitution([pkg_share, "urdf", "microbot.urdf.xacro"])
    control_config = PathJoinSubstitution([pkg_share, "config", "ros2_control.yaml"])
    bridge_config = PathJoinSubstitution([pkg_share, "config", "gz_bridge.yaml"])
    world = LaunchConfiguration("world")
    gui = LaunchConfiguration("gui")
    use_rviz = LaunchConfiguration("use_rviz")
    use_joy = LaunchConfiguration("use_joy")
    spawn_x = LaunchConfiguration("spawn_x")
    spawn_y = LaunchConfiguration("spawn_y")
    spawn_z = LaunchConfiguration("spawn_z")
    joy_config = PathJoinSubstitution([pkg_share, "config", "joy.yaml"])
    rviz_config = PathJoinSubstitution([pkg_share, "rviz", "microbot_sim.rviz"])

    robot_description = {
        "robot_description": ParameterValue(
            Command(
                [
                    "xacro ",
                    xacro_file,
                    " use_ros2_control:=false",
                ]
            ),
            value_type=str,
        )
    }

    spawn_robot = TimerAction(
        period=2.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name",
                    "microbot",
                    "-topic",
                    "robot_description",
                    "-x",
                    spawn_x,
                    "-y",
                    spawn_y,
                    "-z",
                    spawn_z,
                ],
                output="screen",
            )
        ],
    )

    gz_args = [
        PythonExpression(["'-r ' if '", gui, "' == 'true' else '-s -r '"]),
        world,
    ]

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "world",
                default_value=PathJoinSubstitution([pkg_share, "worlds", "arena.sdf"]),
            ),
            DeclareLaunchArgument("gui", default_value="true"),
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("use_joy", default_value="true"),
            DeclareLaunchArgument("spawn_x", default_value="-3.65"),
            DeclareLaunchArgument("spawn_y", default_value="0.0"),
            DeclareLaunchArgument("spawn_z", default_value="0.0"),
            SetEnvironmentVariable(
                name="GZ_SIM_RESOURCE_PATH",
                value=[
                    PathJoinSubstitution([pkg_share, ".."]),
                    ":",
                    EnvironmentVariable("GZ_SIM_RESOURCE_PATH", default_value=""),
                ],
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([ros_gz_sim_share, "launch", "gz_sim.launch.py"])
                ),
                launch_arguments={"gz_args": gz_args}.items(),
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[robot_description, {"use_sim_time": True}],
                output="screen",
            ),
            Node(
                package="joint_state_publisher",
                executable="joint_state_publisher",
                parameters=[robot_description, {"use_sim_time": True}],
                output="screen",
            ),
            spawn_robot,
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                parameters=[{"config_file": bridge_config}],
                output="screen",
            ),
            Node(
                package="joy",
                executable="joy_node",
                name="joy_node",
                parameters=[joy_config],
                condition=IfCondition(use_joy),
                output="screen",
            ),
            Node(
                package="teleop_twist_joy",
                executable="teleop_node",
                name="teleop_twist_joy_node",
                parameters=[joy_config],
                remappings=[("/cmd_vel", "/diff_drive_controller/cmd_vel_unstamped")],
                condition=IfCondition(use_joy),
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                arguments=["-d", rviz_config],
                parameters=[{"use_sim_time": True}],
                condition=IfCondition(use_rviz),
                output="screen",
            ),
        ]
    )
