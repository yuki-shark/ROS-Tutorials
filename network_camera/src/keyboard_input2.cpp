/*
 * Copyright (c) 2011, Willow Garage, Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the Willow Garage, Inc. nor the names of its
 *       contributors may be used to endorse or promote products derived from
 *       this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <ros/ros.h>
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
  double vertical_, horizontal_;
  ros::Time first_publish_;
  ros::Time last_publish_;
  double l_scale_, a_scale_;
  ros::Publisher key_pub_;
  void publish(double, double);
  boost::mutex publish_mutex_;

};

TurtlebotTeleop::TurtlebotTeleop():
  ph_("~"),
  vertical_(0),
  horizontal_(0),
  l_scale_(1.0),
  a_scale_(1.0)
{
  ph_.param("scale_horizontal", a_scale_, a_scale_);
  ph_.param("scale_vertical", l_scale_, l_scale_);

  key_pub_ = nh_.advertise<sensor_msgs::Joy>("cmd_key", 1);
}

int kfd = 0;
struct termios cooked, raw;

void quit(int sig)
{
  tcsetattr(kfd, TCSANOW, &cooked);
  ros::shutdown();
  exit(0);
}


int main(int argc, char** argv)
{
  ros::init(argc, argv, "turtlebot_teleop");
  TurtlebotTeleop turtlebot_teleop;
  ros::NodeHandle n;

  signal(SIGINT,quit);

  boost::thread my_thread(boost::bind(&TurtlebotTeleop::keyLoop, &turtlebot_teleop));


  ros::Timer timer = n.createTimer(ros::Duration(0.1), boost::bind(&TurtlebotTeleop::watchdog, &turtlebot_teleop));

  ros::spin();

  my_thread.interrupt() ;
  my_thread.join() ;

  return(0);
}


void TurtlebotTeleop::watchdog()
{
  boost::mutex::scoped_lock lock(publish_mutex_);
  if ((ros::Time::now() > last_publish_ + ros::Duration(0.15)) &&
      (ros::Time::now() > first_publish_ + ros::Duration(0.50)))
    publish(0, 0);
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

  //add
  // ros::Rate loop = 50;
  while (ros::ok())
    {
      // get the next event from the keyboard
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
      //add
      // loop.sleep();
    }
  return;
}

void TurtlebotTeleop::publish(double horizontal, double vertical)
{
  sensor_msgs::Joy key;
  // key.axes[4] = a_scale_*horizontal;
  // key.axes[5] = l_scale_*vertical;
  // key.axes[4] = horizontal;
  // key.axes[5] = vertical;
  key.axes.resize(6);
  key.axes[0] = 0.0;
  key.axes[1] = 0.0;
  key.axes[2] = horizontal;
  key.axes[3] = vertical;
  key.axes[4] = 0.0;
  key.axes[5] = 0.0;

  key_pub_.publish(key);

  return;
}
