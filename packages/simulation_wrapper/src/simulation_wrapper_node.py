#!/usr/bin/env python3

import os
import rospy
import numpy as np
from cv_bridge import CvBridge

from duckietown.dtros import DTROS, NodeType

from duckietown_msgs.msg import WheelsCmd
from sensor_msgs.msg import Joy
from sensor_msgs.msg import CompressedImage

import gym_duckietown
from gym_duckietown.simulator import Simulator


class SimulationWrapperNode(DTROS):

    def __init__(self, node_name):
        # initialize the DTROS parent class
        super(SimulationWrapperNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        
        # Subscriber for wheel commands
        self.wheel_cmd_sub = rospy.Subscriber('~wheel_cmd', WheelsCmd, self.wheelCmdCB)  # Needs the right topic and message type
        # Subscriber for virtual joystick
        self.joy_sub = rospy.Subscriber('~joy', Joy, self.joyCB)
        # Publisher for images
        self.image_pub = rospy.Publisher('~simulation_images/compressed', CompressedImage, queue_size=10)

        # Action (wheel command) in the simulator
        self.action = np.array([0.0, 0.0])
        # Simulator
        self.env = Simulator(
                seed=123, # random seed
                map_name="loop_empty",
                max_steps=500001, # we don't want the gym to reset itself
                domain_rand=0,
                camera_width=640,
                camera_height=480,
                accept_start_angle_deg=4, # start close to straight
                full_transparency=True,
                distortion=True,
                )   
        # CV and ROS brigde
        self.bridge = CvBridge()

    def wheelCmdCB(self, data):
        vel = np.array([data.vel_left, data.vel_right])
        norm_vel = np.linalg.norm(vel)

        if norm_vel > 1.41:   # Normalize to make values between [-1 1]
            vel = 1.41 * vel / np.linalg.norm(vel)

        self.action = vel
        return

    def joyCB(self, data):
        fore = np.array([0.5, 0.5])
        side = np.array([-0.25, 0.25])

        l_fore = data.axes[1]   # forward = 1, backward = -1
        l_side = data.axes[3]   # left = 1, right = -1

        self.action = l_fore*fore + l_side*side

    def run(self):
        rate = rospy.Rate(30) # 1Hz
        while not rospy.is_shutdown():
            curr_action = self.action
            observation, reward, done, misc = self.env.step(curr_action)
            rgb_img_array = self.env.render(mode='rgb_array')

            if done:
                self.env.reset()

            # Convert to BGR format because that's expected by OpenCV and publish
            img_bgr = np.array(rgb_img_array[...,::-1])
            img_msg = self.bridge.cv2_to_compressed_imgmsg(img_bgr, dst_format='jpeg')
            self.image_pub.publish(img_msg)
            
            rate.sleep()


if __name__ == '__main__':
    # create the node
    node = SimulationWrapperNode(node_name='simulation_wrapper_node')
    node.run()
    # keep spinning
    rospy.spin()
