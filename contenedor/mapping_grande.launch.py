import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace, SetRemap

def generate_launch_description():
    return LaunchDescription([
        Node(package='rviz2',executable='rviz2',arguments=['-d','/ws/contenedor/mapping_office_4.rviz'],parameters=[{'use_sim_time':True}],remappings=[('/tf','/do100_0000/tf'),('/tf_static','/do100_0000/tf_static')]),
        GroupAction([
            PushRosNamespace('do100_0000'),
            SetRemap('/tf','/do100_0000/tf'),SetRemap('/tf_static','/do100_0000/tf_static'),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('slam_toolbox'),'launch','online_sync_launch.py')),launch_arguments={'slam_params_file':'/ws/contenedor/slam_denso.yaml','use_sim_time':'true'}.items())
        ])])
