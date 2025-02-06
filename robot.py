import time
import serial


ser = serial.Serial('/dev/ttyUSB0', 9600)

def go(cm):
  ser.write(("go=" + str(cm) + '\r\n').encode())
  time.sleep(5)

def stop():
  ser.write(("stop" + '\r\n').encode())

def rotate_left():
  ser.write(("rotate_left" + '\r\n').encode())
  time.sleep(5)

def rotate_right():
  ser.write(("rotate_right" + '\r\n').encode())
  time.sleep(5)

