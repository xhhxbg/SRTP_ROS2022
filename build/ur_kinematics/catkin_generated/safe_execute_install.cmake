execute_process(COMMAND "/home/yyf/Documents/SRTP_ROS2022/build/ur_kinematics/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/yyf/Documents/SRTP_ROS2022/build/ur_kinematics/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
