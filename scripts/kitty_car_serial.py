#!/usr/bin/env python
import math
import rospy
import signal
import serial
import sys
import time
from serial import SerialException
from std_msgs.msg import Empty

def signal_handler(signal, frame):
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def connect_to_arduino():
    arduino_port = '/dev/ttyACM'
    arduino_number = 0
    arduino_serial = None
    while arduino_serial is None:
        try:
            arduino_serial = serial.Serial(arduino_port + str(arduino_number), baudrate=115200)
            arduino_serial.flushInput()
            rospy.loginfo('successfully connected to arduino')
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            arduino_number = arduino_number + 1
        if arduino_number > 10:
            rospy.logerr('Failed to open on %s(0-%s) with error: %s' % (arduino_port, str(arduino_number), str(e)))
            time.sleep(1)
            rospy.loginfo('Retrying')
            arduino_number = 0
    return arduino_serial

def toggle_laser():
    arduino_serial.flushInput()
    arduino_serial.write("t\n")
    arduino_serial.flush()

def rotate_feeder():
    arduino_serial.flushInput()
    arduino_serial.write("s\n")
    arduino_serial.flush()

def laser_callback(msg):
    rospy.loginfo("toggling laser")
    toggle_laser()

def feeder_callback(msg):
    rospy.loginfo("rotating feeder")
    rotate_feeder()

rospy.init_node('kitty_car_serial')
arduino_serial = connect_to_arduino()
rospy.Subscriber("laser", Empty, laser_callback)
rospy.Subscriber("feeder", Empty, feeder_callback)

while not rospy.is_shutdown():
    rospy.spin()









