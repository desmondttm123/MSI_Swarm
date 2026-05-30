from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    joy_config = PathJoinSubstitution(
        [FindPackageShare("microbot_description"), "config", "joy.yaml"]
    )

    return LaunchDescription(
        [
            Node(
                package="joy",
                executable="joy_node",
                name="joy_node",
                parameters=[joy_config],
                output="screen",
            ),
            Node(
                package="teleop_twist_joy",
                executable="teleop_node",
                name="teleop_twist_joy_node",
                parameters=[joy_config],
                remappings=[("/cmd_vel", "/diff_drive_controller/cmd_vel_unstamped")],
                output="screen",
            ),
        ]
    )
