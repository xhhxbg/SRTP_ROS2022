#include <ros/ros.h>
#include <pcl/point_cloud.h>
//msgs type and conversion
#include <sensor_msgs/PointCloud2.h>
#include <gazebo_msgs/LinkStates.h>
#include <pcl_conversions/pcl_conversions.h>
//pcd io
#include <pcl/io/pcd_io.h>
//point types
#include <pcl/point_types.h>
#include <message_filters/subscriber.h>
#include <message_filters/synchronizer.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <boost/thread/thread.hpp>
#include <iostream>

int i=0;
char ch=(char)(int('0'));

void pc2_callback(const sensor_msgs::PointCloud2ConstPtr& input)
{
//Convert the sensor_msgs/PointCloud2 data to pcl/PointCloud
  pcl::PointCloud<pcl::PointXYZ> cloud;
  pcl::fromROSMsg (*input, cloud);//cloud is the output
  
//save to PCD for 5 times    
  std::string pcd_name("./pcd/pcl_2_pcd");
  ch++;
  pcd_name+=ch;
  if(pcl::io::savePCDFileASCII (pcd_name+".pcd", cloud)>=0)//input pointcloud should be pcl::PointCloud<PointT> only,rather than others 
  {
    std::cerr << "Saved  " << pcd_name<<".pcd"<< std::endl;
  }
}
 
void pos_callback(const gazebo_msgs::LinkStates& pos)
{
  std::cout << pos.pose[1] << std::endl;
  std::ofstream file("./pcd/info.txt");
  if (file)
  {
      file << pos.pose[1] << "\n";
  }
  file.close();

}

typedef  message_filters::sync_policies::ApproximateTime<sensor_msgs::PointCloud2, gazebo_msgs::LinkStates> syncPolicy;

int main(int argc,char** argv)
{
// Initialize ROS
  ros::init (argc, argv, "pcl_2_pcd");
  ros::NodeHandle nh;
 
// Create a ROS subscriber for the input point cloud
  ros::Subscriber pc2 = nh.subscribe ("/camera/depth/points", 1, pc2_callback);
  ros::Subscriber pos = nh.subscribe ("/gazebo/link_states", 1, pos_callback);

// Spin
  ros::spin ();
}
 