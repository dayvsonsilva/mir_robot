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
import subprocess

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            'mir_type',
            default_value='mir_100',
            description='The MiR variant. Can be "mir_100" or "mir_250" for now.'
        )
    )
    
    declared_arguments.append(
        DeclareLaunchArgument(
            'tf_prefix',
            default_value='',
            description='TF prefix to use for all of the MiR\'s TF frames'
        )
    )

    # Initialize Arguments
    mir_type = LaunchConfiguration('mir_type')
    tf_prefix = LaunchConfiguration('tf_prefix')
    
    # Get package directory
    mir_description_dir = get_package_share_directory('mir_description')
    
    # Prepare URDF file path
    urdf_file = os.path.join(mir_description_dir, 'urdf', 'mir.urdf.xacro')
    
    # Generate robot description using xacro directly
    # This ensures the robot_description parameter is properly populated
    xacro_command = ['xacro', urdf_file, 'mir_type:=mir_100', 'tf_prefix:=']
    robot_description_content = subprocess.check_output(xacro_command).decode('utf-8')
    
    # Robot state publisher node with explicit robot_description content
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True
        }]
    )
    
    # Create and return launch description
    return LaunchDescription(
        declared_arguments + [robot_state_publisher_node]
    )
