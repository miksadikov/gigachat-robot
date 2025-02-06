import sys
import time
import random
import math
import serial

ser = serial.Serial('/dev/ttyS1', 9600, timeout=1)

FSLOW = 45
BSLOW = -45
FFAST = 70
BFAST = -70

time_coeff = 0.6

left_motor1 = brick.motor('M3')
right_motor1 = brick.motor('M4')
left_motor2 = brick.motor('M1')
right_motor2 = brick.motor('M2')


def go(sec):
  left_motor1.setPower(FFAST-7)
  right_motor1.setPower(FFAST+7)
  time.sleep(sec)
  left_motor1.setPower(0)
  right_motor1.setPower(0)

def rotate_left(sec):
  left_motor1.setPower(BSLOW)
  right_motor1.setPower(FSLOW)
  time.sleep(sec)
  left_motor1.setPower(0)
  right_motor1.setPower(0)

def rotate_right(sec):
  left_motor1.setPower(FSLOW)
  right_motor1.setPower(BSLOW)
  time.sleep(sec)
  left_motor1.setPower(0)
  right_motor1.setPower(0)

while True:
  command = ''
  while True:
    oneByte = ser.read(1)
    if oneByte == b"\r":
      break
    else:
      command += oneByte.decode("ascii")

  ser.write(command.encode())
  if command.find('go') != -1:
    splt = command.split("=")
    duration_sec = (float(splt[1])) / 10 * time_coeff
    go(duration_sec)

  elif command.find('rotate_left') != -1:
    rotate_left(3)

  elif command.find('rotate_right') != -1:
    rotate_right(3)

  else:
    ser.write('ok'.encode())
