#include <ros/ros.h>
// #include <geometry_msgs/Twist.h>
#include <sensor_msgs/Joy.h>
#include <signal.h>
#include <termios.h>
#include <stdio.h>
#include "boost/thread/mutex.hpp"
#include "boost/thread/thread.hpp"

#define KEYCODE_R 0x43
#define KEYCODE_L 0x44
#define KEYCODE_U 0x41
#define KEYCODE_D 0x42
#define KEYCODE_Q 0x71

class TurtlebotTeleop
{
public:
  TurtlebotTeleop();
  void keyLoop();
  void watchdog();

private:

  ros::NodeHandle nh_,ph_;
  double horizontal_, vertical_;
  ros::Time first_publish_;
  ros::Time last_publish_;
  // double l_scale_, a_scale_;
  ros::Publisher key_pub_;
  void publish(double, double);
  boost::mutex publish_mutex_;

};


TurtlebotTeleop::TurtlebotTeleop():
  ph_("~"),
  linear_(0),
  angular_(0),
  l_scale_(1.0),
  a_scale_(1.0)
{
  ph_.param("scale_angular", a_scale_, a_scale_);
  ph_.param("scale_linear", l_scale_, l_scale_);

  key_pub_ = nh_.advertise<sensor_msgs::Joy>("cmd_vel", 1);
}


void TurtlebotTeleop::keyLoop()
{
  char c;

  // get the console in raw mode
  tcgetattr(kfd, &cooked);
  memcpy(&raw, &cooked, sizeof(struct termios));
  raw.c_lflag &=~ (ICANON | ECHO);
  // Setting a new line, then end of file
  raw.c_cc[VEOL] = 1;
  raw.c_cc[VEOF] = 2;
  tcsetattr(kfd, TCSANOW, &raw);

  puts("Reading from keyboard");
  puts("---------------------------");
  puts("Use arrow keys to move the turtlebot.");


  while (ros::ok())
    {
      // get the next event from the keyboar
      if(read(kfd, &c, 1) < 0)
        {
          perror("read():");
          exit(-1);
        }

      vertical_=horizontal_=0;
      ROS_DEBUG("value: 0x%02X\n", c);

      switch(c)
        {
        case KEYCODE_L:
          ROS_DEBUG("LEFT");
          horizontal_ = 1.0;
          break;
        case KEYCODE_R:
          ROS_DEBUG("RIGHT");
          horizontal_ = -1.0;
          break;
        case KEYCODE_U:
          ROS_DEBUG("UP");
          vertical_ = 1.0;
          break;
        case KEYCODE_D:
          ROS_DEBUG("DOWN");
          vertical_ = -1.0;
          break;
        }
      boost::mutex::scoped_lock lock(publish_mutex_);
      if (ros::Time::now() > last_publish_ + ros::Duration(1.0)) {
        first_publish_ = ros::Time::now();
      }
      last_publish_ = ros::Time::now();
      publish(horizontal_, vertical_);
    }

  return;
}


void TurtlebotTeleop::publish(double horizontal, double vertical)
{
  // geometry_msgs::Twist vel;
  // vel.angular.z = a_scale_*angular;
  // vel.linear.x = l_scale_*linear;

  sensor_msgs::Joy key;
  key.axis[4] = horizontal;
  key.axis[5] = vertical;

  key_pub_.publish(key);

  return;
}
