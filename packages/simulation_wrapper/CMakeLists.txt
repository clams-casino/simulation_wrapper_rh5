cmake_minimum_required(VERSION 2.8.3)
project(simulation_wrapper)

find_package(catkin REQUIRED COMPONENTS
  rospy
  duckietown_msgs
)

catkin_package()