#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Joy
import urllib2
import time
import cv2

flag = -1
bf_flag = -1

def control_motors(vertical, horizontal):
        global flag
        global bf_flag
        bf_flag = flag
        flag =  -1
        if(abs(horizontal)>0.5 and abs(vertical)>0.5):
                if(horizontal>0 and vertical>0):
                        flag = 90
                elif(horizontal<0 and vertical>0):
                        flag = 91
                elif(horizontal>0 and vertical<0):
                        flag = 92
                else:
                        flag = 93
        elif(vertical>0 and abs(vertical)>abs(horizontal)):
                flag = 0
        elif(vertical<0 and abs(vertical)>abs(horizontal)):
                flag = 2
        elif(horizontal>0 and abs(horizontal)>abs(vertical)):
                flag = 4
        elif(horizontal<0 and abs(horizontal)>abs(vertical)):
                flag = 6
        else:
                if(bf_flag == 0):
                        flag = 1
                elif(bf_flag == 2):
                        flag = 3
                elif(bf_flag == 4):
                        flag = 5
                elif(bf_flag == 6):
                        flag = 7
                elif(bf_flag >= 90):
                        flag = 1
        # rospy.loginfo('==============================================================')
        if(flag==bf_flag):
                pass
        elif(flag>=0):
                urlExecution(flag, -1, -1)
                rospy.loginfo("send URL")
                rospy.loginfo(flag)

def urlExecution(command, param, value):
	timeStamp = int(time.time())*1000
        if(command != -1):
                ip = 'http://192.168.1.123:81/decoder_control.cgi?loginuse=admin&loginpas=12345&command='
                oneStep = '&onestep=0&'
                gibberish = '7485621407675288&_='
                fullURL = ip+str(command)+oneStep+str(timeStamp)+'.49641236611690986&_='+str(timeStamp)
        else:
                ip = 'http://192.168.1.123:81/camera_control.cgi?loginuse=admin&loginpas=12345&param='
                gibberish = '7485621407675288&_='
                fullURL = ip+str(param)+'&value='+str(value)+'&'+str(timeStamp)+'.49641236611690986&_='+str(timeStamp)
        rospy.loginfo(fullURL)
	response = urllib2.urlopen(fullURL)

def callback(data):
	# rospy.loginfo(data)
	# rospy.loginfo('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	horizontal = data.axes[2]
	vertical = data.axes[3]
	control_motors(vertical,horizontal)

        # rospy.loginfo(horizontal)
        # rospy.loginfo(vertical)

#	rospy.loginfo('X: ' + str(data.data[9]))
#	rospy.loginfo('Y: ' + str(data.data[10]))
#	control_motors(error_x,error_y);


def listener():
    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('object_tracking', anonymous=True)

    rospy.Subscriber("/joy", Joy, callback)

    # set FrameRate
    rospy.loginfo("set FrameRate")
    urlExecution(-1, 6, 30)
    # set PTZ speed
    rospy.loginfo("set PTZ speed")
    urlExecution(-1, 100, 10)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
