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
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Declare arguments
    declared_arguments = []
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
    
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_laser_filter',
            default_value='false',
            description='Whether to use the rep117_filter.py from mir_driver package (set to false if mir_driver is not available)'
        )
    )
    
    # Initialize Arguments
    robot_x = LaunchConfiguration('robot_x')
    robot_y = LaunchConfiguration('robot_y')
    robot_yaw = LaunchConfiguration('robot_yaw')
    tf_prefix = LaunchConfiguration('tf_prefix')
    use_laser_filter = LaunchConfiguration('use_laser_filter')
    
    # Define prefix logic
    prefix = tf_prefix
    model_name = 'mir'
    
    # Get package directories
    mir_description_dir = get_package_share_directory('mir_description')
    mir_gazebo_dir = get_package_share_directory('mir_gazebo')
    
    # Removido o nó robot_state_publisher duplicado
    # O robot_state_publisher já é lançado no arquivo principal mir_gazebo_launch.py
    
    # Spawn the robot into Gazebo
    spawn_urdf_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-entity', model_name,
            '-topic', 'robot_description',
            '-x', robot_x,
            '-y', robot_y,
            '-z', '0.01',
            '-Y', robot_yaw
        ],
        output='screen'
    )
    
    # Load ros2_control node
    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'use_sim_time': True},
            os.path.join(mir_gazebo_dir, 'config', 'mir_controllers.yaml')
        ],
        output='screen'
    )
    
    # Load ros_control controller configurations
    controller_spawner_node = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_controller', 'mobile_base_controller'],
        output='screen'
    )
    
    # Add passive + mimic joints to joint_states topic
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{'source_list': ['mir/joint_states'], 'rate': 200.0}]
    )
    
    # Load teleop
    rqt_robot_steering_node = Node(
        package='rqt_robot_steering',
        executable='rqt_robot_steering',
        parameters=[
            {'default_topic': 'cmd_vel'},
            {'default_vx_max': 1.0},
            {'default_vx_min': -1.0},
            {'default_vw_max': 1.5},
            {'default_vw_min': -1.5}
        ]
    )
    
    # Create combined scan topic (like on real MiR)
    b_scan_relay_node = Node(
        package='topic_tools',
        executable='relay',
        name='b_scan_relay',
        arguments=['b_scan', 'scan']
    )
    
    f_scan_relay_node = Node(
        package='topic_tools',
        executable='relay',
        name='f_scan_relay',
        arguments=['f_scan', 'scan']
    )
    
    # Optional laser filter nodes - only used if mir_driver is available and use_laser_filter is true
    b_rep117_laser_filter_node = Node(
        condition=IfCondition(use_laser_filter),
        package='mir_driver',
        executable='rep117_filter.py',
        name='b_rep117_laser_filter',
        remappings=[
            ('scan', 'b_scan'),
            ('scan_filtered', 'b_scan_rep117')
        ],
        output='screen'
    )
    
    f_rep117_laser_filter_node = Node(
        condition=IfCondition(use_laser_filter),
        package='mir_driver',
        executable='rep117_filter.py',
        name='f_rep117_laser_filter',
        remappings=[
            ('scan', 'f_scan'),
            ('scan_filtered', 'f_scan_rep117')
        ],
        output='screen'
    )
    
    # Create and return launch description
    return LaunchDescription(
        declared_arguments + [
            # robot_state_publisher_node, # Removido para evitar duplicidade
            spawn_urdf_node,
            controller_manager_node,  # Primeiro lançar o controller_manager
            controller_spawner_node,  # Depois lançar o spawner
            joint_state_publisher_node,
            rqt_robot_steering_node,
            b_scan_relay_node,
            f_scan_relay_node,
            b_rep117_laser_filter_node,
            f_rep117_laser_filter_node
        ]
    )
