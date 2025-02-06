import os
import sys
import cv2
import torch
import time
import numpy as np
from ultralytics import YOLO


colors = [(255, 0, 0), (0, 0, 255)]

# https://pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/
camera_coefficient = 1687
objects_sizes = {'chair': 0.4}

number_of_camera = 0

camera = cv2.VideoCapture(number_of_camera)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if camera.isOpened() != True:
  print("USB Camera Open Error!!!")
  sys.exit(0)

#model = YOLO('yolov5su.pt')
model = YOLO('yolov8s.pt')

def capture():
  while True:
    print('== capture ==')
    ret, image = camera.read()
    if ret:
      if os.path.isfile('/tmp/image.jpg'):
        os.remove('/tmp/image.jpg')
        time.sleep(1)
      cv2.imwrite('/tmp/image.jpg', image)
    if ret:
      break
  return image


def object_detection(image, our_class):
  print('== object detection... ==')
  object_detected = False
  our_color = (0, 128, 0)
  img = cv2.imread('/tmp/image.jpg')
  results = model(img)[0]
  color_for_bbox = (0, 128, 0) # зеленый
  img = results.orig_img
  #image = cv2.imread('/tmp/image.jpg')
  classes_names = results.names
  classes = results.boxes.cls.cpu().numpy()
  boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

  # Подготовка словаря для группировки результатов по классам
  grouped_objects = {}

  # Рисование рамок и группировка результатов
  for class_id, box in zip(classes, boxes):
    class_name = classes_names[int(class_id)]
    color = colors[int(class_id) % len(colors)]
    if (class_name == our_class):
      print('== object detected! ==')
      color = our_color
      object_detected = True
    if class_name not in grouped_objects:
      grouped_objects[class_name] = []
      grouped_objects[class_name].append(box)

    # Рисование рамок на изображении
    x1, y1, x2, y2 = box
    frame_thickness = 2
    if (class_name == our_class):
      frame_thickness = 10
    cv2.rectangle(img, (x1, y1), (x2, y2), color, frame_thickness)
    cv2.putText(img, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

  if os.path.isfile('/tmp/image2.jpg'):
    os.remove('/tmp/image2.jpg')
    time.sleep(1)
  cv2.imwrite('/tmp/image2.jpg', img)
  time.sleep(1)
  return object_detected, img


def find_green_bbox_width(image):
  print('== find_green_bbox_width ==')
  # Преобразование в цветовое пространство HSV для более легкого определения цвета
  hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

  # Диапазон зеленого цвета в HSV
  lower_green = np.array([40, 50, 50])
  upper_green = np.array([80, 255, 255])

  # Создаем маску для зеленого цвета
  mask = cv2.inRange(hsv, lower_green, upper_green)

  # Находим контуры маски
  contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  # Находим наибольший контур (предполагая, что это ограничивающая рамка)
  cnt = max(contours, key=cv2.contourArea)

  # Получаем ограничивающий прямоугольник контура
  x, y, w, h = cv2.boundingRect(cnt)

  # Вычисляем центр ограничивающего прямоугольника
  center_x = x + w // 2
  center_y = y + h // 2
  print('width = ', w)
  return center_x, center_y, w


def get_object_distance(class_name, object_width_px):
  print('== get_object_distance ==')
  object_width_m = objects_sizes.get(class_name)
  distance = ((object_width_m * camera_coefficient) / object_width_px) * 100
  print('distance = ', distance)
  return distance


def object_center_offset(object_x):
  offset = abs(960 - object_x)
  print('смещение от центра объекта = ' + str(offset) + ' пикселей')
  if offset < 500:
      return True
  else:
      return False
