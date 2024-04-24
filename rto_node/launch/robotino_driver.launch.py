# Author: Saurabh Borse(saurabh.borse@alumni.fh-aachen.de)

#  MIT License
#  Copyright (c) 2023 Saurabh Borse
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:

#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.

#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

#!/usr/bin/env python

import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, OpaqueFunction, GroupAction
from launch.substitutions import LaunchConfiguration
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.conditions import IfCondition
import launch
from launch.substitutions import LaunchConfiguration, Command


def launch_nodes_withconfig(context, *args, **kwargs):
    
    # Declare launch configuration variables
    namesapce = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    launch_jsb = LaunchConfiguration('launch_jsb')
    robot_description = LaunchConfiguration('robot_description')
    hostname = LaunchConfiguration('hostname')
    
    launch_configuration = {}
    for argname, argval in context.launch_configurations.items():
        launch_configuration[argname] = argval
        
    tf_prefix = launch_configuration['namespace']+'/'
    
    frame_id_baselink = tf_prefix+'base_link'
    frame_id_irscan = tf_prefix+'irpcl_link'
    frame_id_irpcl = tf_prefix+'irscan_link'
    frame_id_imu = tf_prefix+'imu_link'

    # launch robotinobase controllers with individual namespaces
    launch_nodes = GroupAction(
        actions=[
        
        # Launch robotino driver node
        Node(
            package='rto_node',
            executable='rto_node',
            name='robotino_node',
            namespace=namesapce,
            parameters=[{
                'hostname' : hostname,
                'tf_prefix' : tf_prefix,
            }]
        ), 
        
        # Initialize robot state publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            namespace=namesapce,
            parameters=[{'robot_description': Command(["xacro ", robot_description]),
                        'use_sim_time': use_sim_time,
                        'publish_frequency': 20.0,
                        'frame_prefix': tf_prefix}],
        ),
        
        # Initialize Static TF publishers
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=['0.0', '0.0', '0.05', '0.0', '0.0', '0.0', frame_id_baselink,frame_id_irscan],
        ),
        
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=['0.0', '0.0', '0.05', '0.0', '0.0', '0.0', frame_id_baselink,frame_id_irpcl],
        ),
        
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=['0.0', '0.0', '0.10', '0.0', '0.0', '0.0', frame_id_baselink,frame_id_imu],
        ),
        
        # Initialize joint state broadcaster
        Node(
            package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_publisher",
            namespace=namesapce,
            remappings=[("robot_description", '/'+launch_configuration['namespace']+"/robot_description"),
                        ("joint_states", '/'+launch_configuration['namespace']+"/joint_states")],
            condition = IfCondition(launch_jsb),
        )     
    ])
    
    return[launch_nodes]

def generate_launch_description():
    package_dir = get_package_share_directory('rto_node')
    
    # Declare launch configuration variables
    declare_namespace_argument = DeclareLaunchArgument(
        'namespace', default_value='',
        description='Top-level namespace')

    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation clock if true')
    
    declare_launch_rviz_argument = DeclareLaunchArgument(
        'launch_jsb',
        default_value='false', 
        description= 'Wheather to start Rvizor not based on launch environment')
    
    declare_robot_description_config_argument = DeclareLaunchArgument(
        'robot_description',default_value=os.path.join(package_dir, "urdf/robots/robotino_description.urdf"),
        description='Full path to mps_config.yaml file to load')
    
    declare_namespace_argument = DeclareLaunchArgument(
        'hostname', default_value='172.26.108.84:12080',
        description='ip addres of robotino')

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_namespace_argument)
    ld.add_action(declare_use_sim_time_argument)
    ld.add_action(declare_launch_rviz_argument)
    ld.add_action(declare_robot_description_config_argument)
    
    # Add the actions to launch webots, controllers and rviz
    ld.add_action(OpaqueFunction(function=launch_nodes_withconfig))
    
    return ld