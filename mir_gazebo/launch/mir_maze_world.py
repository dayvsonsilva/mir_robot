# Copyright (c) 2018-2022, Martin Günther (DFKI GmbH) and contributors
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            'gui',
            default_value='true',
            description='Set to "false" to run headless.'
        )
    )
    
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_x',
            default_value='0.0',
            description='Spawning position of robot (x)'
        )
    )
    
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_y',
            default_value='0.0',
            description='Spawning position of robot (y)'
        )
    )
    
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_yaw',
            default_value='0.0',
            description='Spawning position of robot (yaw)'
        )
    )
    
    declared_arguments.append(
        DeclareLaunchArgument(
            'tf_prefix',
            default_value='',
            description='tf_prefix to be used by gazebo plugins and in the robot\'s urdf etc.'
        )
    )
    
    # Initialize Arguments
    gui = LaunchConfiguration('gui')
    robot_x = LaunchConfiguration('robot_x')
    robot_y = LaunchConfiguration('robot_y')
    robot_yaw = LaunchConfiguration('robot_yaw')
    tf_prefix = LaunchConfiguration('tf_prefix')
    
    # Get package directories
    ros_gz_sim_dir = get_package_share_directory('ros_gz_sim')
    mir_gazebo_dir = get_package_share_directory('mir_gazebo')
    
    # Launch Gazebo with maze world
    gz_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim_dir, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': ['-r -s -v4 ', os.path.join(mir_gazebo_dir, 'worlds', 'maze.world')],
            'on_exit_shutdown': 'true',
            'gui': gui
        }.items()
    )
    
    # Spawn maze model
    spawn_maze_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-sdf',
            '-file', os.path.join(mir_gazebo_dir, 'sdf', 'maze', 'model.sdf'),
            '-name', 'walls'
        ],
        output='screen'
    )
    
    # Launch MiR Gazebo common
    mir_gazebo_common_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(mir_gazebo_dir, 'launch', 'include', 'mir_gazebo_common.py')),
        launch_arguments={
            'robot_x': robot_x,
            'robot_y': robot_y,
            'robot_yaw': robot_yaw,
            'tf_prefix': tf_prefix
        }.items()
    )
    
    # Create and return launch description
    return LaunchDescription(
        declared_arguments + [
            gz_sim_launch,
            spawn_maze_node,
            mir_gazebo_common_launch
        ]
    )
