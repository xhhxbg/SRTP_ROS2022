# 开启GAZEBO仿真
roslaunch ur_gazebo ur5.launch
# 开启Moveit规划器
roslaunch ur5_moveit_config ur5_moveit_planning_execution.launch sim:=true limited:=true
# 轨迹控制程序
rosrun srtp_pcreg ur5moveit.py 0
# rviz view

# 0 原模型方向
rosservice call gazebo/set_model_state '{model_state: {model_name: arm_part, pose: {position: { x: 0.0, y: 0.0, z: 0.0 }, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}'

# 1 旋转90度
rosservice call gazebo/set_model_state '{model_state: {model_name: arm_part, pose: {position: { x: 0.0, y: 0.0, z: 0.0 }, orientation: {x: 0.0, y: 0.0, z: 0.707, w: 0.707}}}}'

# 2 旋转180度
rosservice call gazebo/set_model_state '{model_state: {model_name: arm_part, pose: {position: { x: 0.0, y: 0.0, z: 0.0 }, orientation: {x: 0.0, y: 0.0, z: 1, w: 0.0}}}}'

# 3 旋转-90度
rosservice call gazebo/set_model_state '{model_state: {model_name: arm_part, pose: {position: { x: 0.0, y: 0.0, z: 0.0 }, orientation: {x: 0.0, y: 0.0, z: -0.707, w: 0.707}}}}'