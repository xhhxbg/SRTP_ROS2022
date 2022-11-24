import rospy, sys
import moveit_commander
from geometry_msgs.msg import PoseStamped, Pose
from tf.transformations import quaternion_from_euler
from math import pi
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
from gazebo_msgs.srv import *
from threading import Thread
from sensor_msgs.msg import PointCloud2
import sensor_msgs.point_cloud2 as pc2
import pcl
import os

class MoveItIkDemo:
    def __init__(self):
        # 初始化move_group的API
        moveit_commander.roscpp_initialize(sys.argv)
        
        # 初始化ROS节点
        rospy.init_node('moveit_ik_demo')
        

        # position_0 = [(-2, 0, 0.1), (2, 0, 0.1), (0, -2, 0.1), (0, 2, 0.1)]
        # self.x0, self.y0, self.z0 = position_0[int(sys.argv[1])]
        self.x0, self.y0, self.z0 = (-0.8, 0, 0.01)
        self.image_index = 0
        self.depth_index = 0
        self.bridge = CvBridge()
        self.path = "/home/yyf/Documents/ros_srtp/pcd/" + sys.argv[1] + "/"
        self.depth_capture_flag = 0
        self.capture_done = 0
        self.poses = []
        # rospy.Subscriber('/camera/depth/image_raw', Image, self.depth_callback)
        # rospy.Subscriber('/camera/rgb/image_raw', Image, self.image_callback)
        rospy.Subscriber('/camera/depth/points', PointCloud2, self.pc_callback)

        th = Thread(target=rospy.spin)
        th.start()


        # 初始化需要使用move group控制的机械臂中的arm group
        self.arm = moveit_commander.MoveGroupCommander('manipulator')
                
        # 获取终端link的名称，这个在setup assistant中设置过了
        # self.end_effector_link = self.arm.get_end_effector_link()
        self.end_effector_link = "camera_link"
        

        # 设置目标位置所使用的参考坐标系
        self.reference_frame = 'base_link'
        self.arm.set_pose_reference_frame(self.reference_frame)
                
        # 当运动规划失败后，允许重新规划
        self.arm.allow_replanning(True)
        
        # 设置位置(单位：米)和姿态（单位：弧度）的允许误差
        self.arm.set_goal_position_tolerance(0.001)
        self.arm.set_goal_orientation_tolerance(0.01)
       
        # 设置允许的最大速度和加速度
        self.arm.set_max_acceleration_scaling_factor(0.5)
        self.arm.set_max_velocity_scaling_factor(0.5)

        print("set")
        rospy.wait_for_service('/gazebo/set_model_state')
 
        set_state_service = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)
        objstate = SetModelStateRequest()  # Create an object of type SetModelStateRequest
        
        # set red cube pose
        orirntations = [
            (0.0, 0.0, 0.0, 1.0), 
            (0.0, 0.0, 0.707, 0.707), 
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, -0.707, 0.707)
        ]

        objstate.model_state.model_name = "arm_part"
        objstate.model_state.pose.position.x = 0.0
        objstate.model_state.pose.position.y = 0.0
        objstate.model_state.pose.position.z = 0.0
        objstate.model_state.pose.orientation.x, \
        objstate.model_state.pose.orientation.y, \
        objstate.model_state.pose.orientation.z, \
        objstate.model_state.pose.orientation.w = orirntations[int(sys.argv[1])]
        objstate.model_state.twist.linear.x = 0.0
        objstate.model_state.twist.linear.y = 0.0
        objstate.model_state.twist.linear.z = 0.0
        objstate.model_state.twist.angular.x = 0.0
        objstate.model_state.twist.angular.y = 0.0
        objstate.model_state.twist.angular.z = 0.0
        objstate.model_state.reference_frame = "world"

        result = set_state_service(objstate)


    def set_position(self, x, y, z):
        # 设置机械臂工作空间中的目标位姿，位置使用x、y、z坐标描述，
        # 姿态使用四元数描述，基于base_link坐标系
        target_pose = PoseStamped()
        #参考坐标系，前面设置了
        target_pose.header.frame_id = self.reference_frame
        target_pose.header.stamp = rospy.Time.now() #时间戳？
        #末端位置   
        target_pose.pose.position.x = x
        target_pose.pose.position.y = y
        target_pose.pose.position.z = z
        #末端姿态，四元数
        target_pose.pose.orientation.x, \
        target_pose.pose.orientation.y, \
        target_pose.pose.orientation.z, \
        target_pose.pose.orientation.w = self.calc_orientation(x, y, z)
        # angle = quaternion_from_euler(a1, a2, a3)
        # target_pose.pose.orientation.x = angle[0]
        # target_pose.pose.orientation.y = angle[1]
        # target_pose.pose.orientation.z = angle[2]
        # target_pose.pose.orientation.w = angle[3]
        
        # 设置机器臂当前的状态作为运动初始状态
        self.arm.set_start_state_to_current_state()
        
        # 设置机械臂终端运动的目标位姿
        self.arm.set_pose_target(target_pose, self.end_effector_link)
        
        # 规划运动路径，返回虚影的效果
        plan_success, traj, planning_time, error_code = self.arm.plan()

        # 按照规划的运动路径控制机械臂运动
        self.arm.execute(traj)
        # rospy.sleep(1)  #执行完成后休息1s

    def init(self):
        # 控制机械臂回到初始化位置
        self.arm.set_named_target('home')
        self.arm.go()
        rospy.sleep(1)
        print(self.arm.get_current_pose(self.end_effector_link).pose)

    def close(self):
        # 关闭并退出moveit
        moveit_commander.roscpp_shutdown()
        moveit_commander.os._exit(0)

    def calc_orientation(self, x1, y1, z1):
        orient0 = np.array([1, 0, 0])
        orient1 = np.array([-(self.x0 + x1), -(self.y0 + y1), -(self.z0 + z1)])
        n = np.cross(orient0, orient1) / np.linalg.norm(np.cross(orient0, orient1))
        a = np.arctan2(np.linalg.norm(np.cross(orient0, orient1)), np.dot(orient0, orient1))
        return n[0]*np.sin(a/2), n[1]*np.sin(a/2), n[2]*np.sin(a/2), np.cos(a/2)

    def pause_and_capture(self):
        rospy.sleep(2)
        self.depth_capture_flag = 1
        print('capture waiting...')
        while self.capture_done == 0:
            continue
        self.capture_done = 0
        print('capture done!')
        self.poses.append(self.arm.get_current_pose(self.end_effector_link).pose)

    def set_group_1(self, h, r, step, if_capture=True):

        start_theta = -np.pi/4
        target_theta = np.pi/4
        step_num = step
        step = (target_theta - start_theta) / step_num
        for i in range(step_num+1):
            x = -(self.x0 + r * np.cos(start_theta + i * step))
            y = -(self.y0 + r * np.sin(start_theta + i * step))
            z = h
            self.set_position(x, y, z)
            rospy.sleep(1)
            if if_capture:
                self.pause_and_capture()
          
    def pc_callback(self, msg):
        if(self.depth_capture_flag):
            print("begin capture!")
            self.depth_capture_flag = 0
            pc_name = "frame-%02d.pcd"%(self.depth_index) #图像命名：时间戳.jpg
            self.ros_to_pcl(msg, self.path + "origin/" + pc_name)
            self.depth_index += 1

    def ros_to_pcl(self, ros_cloud, filename):
        """ Converts a ROS PointCloud2 message to a pcl PointXYZRGB

            Args:
                ros_cloud (PointCloud2): ROS PointCloud2 message

            Returns:
                pcl.PointCloud_PointXYZRGB: PCL XYZRGB point cloud
        """

        points_list = []
        points_str = []
        for data in pc2.read_points(ros_cloud, skip_nans=True):
            points_list.append([data[0], data[1], data[2], data[3]])
        
        #写文件句柄
        handle = open(filename, 'w')
        
        #得到点云点数
        point_num=len(points_list)
        print('num: ', point_num)

        #pcd头部（重要）
        handle.write('# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1')
        string = '\nWIDTH ' + str(point_num)
        handle.write(string)
        handle.write('\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0')
        string = '\nPOINTS ' + str(point_num)
        handle.write(string)
        handle.write('\nDATA ascii')
        handle.write('\n')
        # 依次写入点
        # for i in range(point_num):
        #     string = '\n' + str(points_list[i][0]) + ' ' \
        #         + str(points_list[i][1]) + ' ' \
        #         + str(points_list[i][2])
        #     handle.write(string)
        for point in points_list:
            stp = str(point[0]) + ' ' \
                + str(point[1]) + ' ' \
                + str(point[2])
            points_str.append(stp)

        handle.write('\n'.join(points_str))
            
        handle.close()
        print(filename, 'save done!')
        self.capture_done = 1

    def save_data(self):
        handle = open(self.path + "data.txt", 'w')
        for pose in self.poses:
            string = \
                str(pose.position.x) + ' ' + \
                str(pose.position.y) + ' ' + \
                str(pose.position.z) + ' ' + \
                str(pose.orientation.x) + ' ' + \
                str(pose.orientation.y) + ' ' + \
                str(pose.orientation.z) + ' ' + \
                str(pose.orientation.w) 
            handle.write(string + "\n")
        handle.close()

if __name__ == "__main__":
    moveit = MoveItIkDemo()
    moveit.init()
    # moveit.set_group_1(0.3, 0.4, 3, True)
    moveit.set_group_1(0.5, 0.3, 3, True)
    moveit.init()
    moveit.save_data()
    moveit.close()