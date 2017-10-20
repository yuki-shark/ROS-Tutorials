#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Joy
import urllib2
import time 
import cv2

flag = -1
bf_flag = -1
_isSleep = 0

# def generate_flag(vertical, horizontal):
#         bf_flag = flag
#         flag =  -1
#         if(horizontal>0 and abs(horizontal)>abs(vertical)):
#                 flag = 0
#         elif(horizontal<0 and abs(horizontal)>abs(vertical)):
#                 flag = 2
#         elif(vertical>0 and abs(vertical)>abs(horizontal)):
#                 flag = 4
#         elif(vertical<0 and abs(vertical)>abs(horizontal)):
#                 flag = 6
#         else:
#                 flag = -1
#                 if(bf_flag == 0):
#                         flag = 1
#                 elif(bf_flag == 2):
#                         flag = 3
#                 elif(bf_flag == 4):
#                         flag = 5
#                 elif(bf_flag == 6):
#                         flag = 7

def control_motors(vertical, horizontal):
        # generate_flag(vertical,horizontal)
        global flag
        global bf_flag
        global _isSleep
        bf_flag = flag
        flag =  -1
        if(horizontal>0 and abs(horizontal)>abs(vertical)):
                flag = 0
        elif(horizontal<0 and abs(horizontal)>abs(vertical)):
                flag = 2
        elif(vertical>0 and abs(vertical)>abs(horizontal)):
                flag = 4
        elif(vertical<0 and abs(vertical)>abs(horizontal)):
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
        rospy.loginfo('==============================================================')
        if(flag==bf_flag):
                # _isSleep = 1
                # time.sleep(0.1)
                # _isSleep = 0
                rospy.loginfo('sleep')
                rospy.loginfo(flag)
        elif(flag>=0):
                urlExecution(flag)
                # if(flag==0):
                #         urlExecution(0)
                # elif(flag==1):
                #         urlExecution(1)
                # elif(flag==2):
                #         urlExecution(2)
                # elif(flag==3):
                #         urlExecution(3)
                # elif(flag==4):
                #         urlExecution(4)
                # elif(flag==5):
                #         urlExecution(5)
                # elif(flag==6):
                #         urlExecution(6)
                # elif(flag==7):
                #         urlExecution(7)
                rospy.loginfo("send URL")
                rospy.loginfo(flag)

def urlExecution(command):
	ip = 'http://192.168.1.6:81/decoder_control.cgi?loginuse=admin&loginpas=12345&command='
	oneStep = '&onestep=1&'
	gibberish = '7485621407675288&_='
	timeStamp = int(time.time())*1000
	fullURL = ip+str(command)+oneStep+str(timeStamp)+'.49641236611690986&_='+str(timeStamp)
        rospy.loginfo(fullURL)
	response = urllib2.urlopen(fullURL)

def callback(data):
	# rospy.loginfo(data)
	# rospy.loginfo('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	horizontal = data.axes[0]
	vertical = data.axes[1]
	control_motors(vertical,horizontal)
        rospy.loginfo(horizontal)
        rospy.loginfo(vertical)
		
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
