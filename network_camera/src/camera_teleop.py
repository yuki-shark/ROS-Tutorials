#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Joy
import urllib2
import time 
import cv2

horizontal_flag = False
vertical_flag = False
bf_horizontal_flag = False
bf_vertical_flag = False

control_flag = False
bf_control_flag = False

zero_flag = [0,0,0,0,0,0,0,0]
flag = [0,0,0,0,0,0,0,0]
bf_flag = [0,0,0,0,0,0,0,0]

def abs(num):
        if num<0:
                num *= -1
        return num

def generate_flag(vertical, horizontal):
        bf_flag = flag
        flag = zero_flag
        if(horizontal>0 && abs(horizontal)>abs(vertical)):
                flag[0] = 1
        elif(horizontal<0 && abs(horizontal)>abs(vertical)):
                flag[2] = 1
        elif(vertical>0 && abs(vertical)>abs(horizontal)):
                flag[4] = 1
        elif(vertical<0 && abs(vertical)>abs(horizontal)):
                flag[6] = 1
        else:
                if(bf_flag[0]==1):
                        flag[1] = 1
                elif(bf_flag[2]==1):
                        flag[3] = 1
                elif(bf_flag[4]==1):
                        flag[5] = 1
                elif(bf_flag[6]==1):
                        flag[7] = 1


def control_motors(vertical, horizontal):
        if(!bf_control_flag && control_flag):
                if(horizontal>0):
                        urlExecution(4)
                        time.sleep(0.1)
                elif(horizontal<0):
                        urlExecution(6)
                        time.sleep(0.1)
                if(vertical>0):
                        urlExecution(0)
                        time.sleep(0.1)
                elif(vertical<0):
                        urlExecution(2)
                        time.sleep(0.1)
        if(bf_control_flag && control_flag):
               i f(horizontal>0):
                        time.sleep(0.1)
                elif(horizontal<0):
                        time.sleep(0.1)
                if(vertical>0):
                        time.sleep(0.1)
                elif(vertical<0):
                        time.sleep(0.1)
        if(bf_control_flag && !control_flag):
        	if(bf_horizontal>0):
                        urlExecution(5)
                elif(bf_horizontal<0):
                        urlExecution(7)
                if(bf_vertical>0):
                        urlExecution(1)
                elif(bf_vertical<0):
                        urlExecution(3)

def urlExecution(command):
	ip = 'http://192.168.1.6:81/decoder_control.cgi?loginuse=admin&loginpas=12345&command='
	oneStep = '&onestep=1&'
	gibberish = '7485621407675288&_='
	timeStamp = int(time.time())*1000
	fullURL = ip+str(command)+oneStep+str(timeStamp)+'.49641236611690986&_='+str(timeStamp)
	response = urllib2.urlopen(fullURL)
	rospy.loginfo(fullURL)

def callback(data):
	rospy.loginfo(data)
	rospy.loginfo('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	horizontal = data.axes[0]
	vertical = data.axes[1]
        # if(horizontal == 0.0):
        #         horizontal_flag = False
        # else:
        #         horizontal_flag = True
        # if(vertical == 0.0):
        #         vertical_flag = False
        # else:
        #         vertical_flag = True
        bf_control_flag = control_flag
        if(control == 0.0 && vertical == 0.0):
                control_flag = False
        else:
                control_flag = True
	control_motors(vertical,horizontal)
        
		
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

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
