import time
from cv2 import CAP_PROP_CONTRAST, CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH
import numpy as np
import cv2
import math

from torch import le

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
cv2.useOptimized()

image_height = 0
iterator = 0
last_perf_counter = time.perf_counter()
current_throttle_time = 0
debug_added_nodes = 0

class tracked_eye:
    def __init__(self, cx, cy):
        self.age = 0
        self.dead_ticks = 0
        self.referenced = 0
        self.cx = cx
        self.cy = cy
        self.spb = 3.000
        self.last_timer = -1

    def __str__(self):
        return f'[{self.cx} {self.cy}]'

    def update(self, x, y, w, h):
        if math.sqrt(pow(self.cx-(x+w/2), 2) + pow(self.cy-(y+h/2), 2)) < 120:
            self.cx = x+w/2
            self.cy = y+h/2
            self.dead_ticks = 0
            self.referenced += 1
            return 1
        else:
            return 0

    def no_reference_warning(self):
        self.dead_ticks += 1

    def reset(self):
        self.referenced = 0
        self.age += 1


tracked_eye_list = []

# number signifies camera
cap = cv2.VideoCapture(0)
cap.set(CAP_PROP_FRAME_WIDTH, 1280)
cap.set(CAP_PROP_FRAME_HEIGHT, 720)
cap.set(CAP_PROP_CONTRAST, 50)
print(f'Camera resolution: {cap.get(CAP_PROP_FRAME_WIDTH)} x {cap.get(CAP_PROP_FRAME_HEIGHT)} / Contrast: {cap.get(CAP_PROP_CONTRAST)}')


while 1:
    blink_interval = 3.0
    
# your code execution
    e1 = cv2.getTickCount()
    ret, img = cap.read()
    current_blink_time_sum = 0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) > 0:
        face0 = faces[0:1]
        fx1=int(face0.item(0))
        fy1=int(face0.item(1))
        fx2=fx1+int(face0.item(2))
        fy2=fy1+int(face0.item(3))
        cv2.rectangle(img, (fx1, fy1), (fx2, fy2), (0, 0, 255), 2)
        grey2 = gray[fy1:fy2, fx1:fx2]
    else:
        fx1=0
        fy1=0
        fx2=CAP_PROP_FRAME_WIDTH
        fy2=CAP_PROP_FRAME_HEIGHT
        grey2=gray
    eyes = eye_cascade.detectMultiScale(grey2, 1.3, 5)
    # print(f'{len(faces)} faces ({faces}), {len(eyes)} eyes ({eyes})', end='                                              \r')
    e2 = cv2.getTickCount()
    cv_time = (e2 - e1)/ cv2.getTickFrequency()
    for (ex, ey, ew, eh) in eyes:
        if ex == 0 or ey == 0 or ey == 0:
            continue

        ex = int(ex)
        ey = int(ey)
        ew = int(ew)
        eh = int(eh)

        cv2.rectangle(img, (fx1+ex, fy1+ey), (fx1+ex+ew, fy1+ey+eh), (0, 255, 0), 2)
        if(len(tracked_eye_list) <= 0):
            tracked_eye_list.append(tracked_eye(ex+ew/2, ey+eh/2))
            debug_added_nodes += 1
        else:
            activated_count = 0
            for eye_entity in tracked_eye_list:
                code = eye_entity.update(ex, ey, ew, eh)
                if code == 1:
                    activated_count += 1
                    break
            if activated_count == 0:
                tracked_eye_list.append(tracked_eye(ex+ew/2, ey+eh/2))
                debug_added_nodes += 1

    eye_eligible_count = 0
    for eye_entity in tracked_eye_list:
        if eye_entity.referenced <= 0:
            eye_entity.no_reference_warning()
            cv2.circle(img, (fx1+int(eye_entity.cx), fy1+int(
            eye_entity.cy)), 12, (0, 0, 255), 2)
        else:
            cv2.circle(img, (fx1+int(eye_entity.cx), fy1+int(
            eye_entity.cy)), 12, (255, 0, 0), 2)
        if eye_entity.dead_ticks == 3:
            if eye_entity.last_timer == -1:
                eye_entity.last_timer = time.perf_counter()
                
            else:
                eye_entity.spb = (
                    eye_entity.spb * 5 + (time.perf_counter() - eye_entity.last_timer))/6
                eye_entity.last_timer = time.perf_counter()
        if eye_entity.dead_ticks > 30:
            tracked_eye_list.remove(eye_entity)
            continue
        if(eye_entity.age > 30):
            eye_eligible_count += 1
            current_blink_time_sum += eye_entity.spb
        eye_entity.reset()
        # print(f'[{eye_entity.cx} {eye_entity.cy}]', end=' / ')

    if(eye_eligible_count > 0):
        blink_interval = current_blink_time_sum / eye_eligible_count
        if blink_interval == 0:
            blink_interval = 3
    
    # print(f'blink_interval: ', end=' / ')
    if iterator % 10 == 0 and iterator > 10:
        this_perf_counter = time.perf_counter()
        print(f'{round(blink_interval,2)}spb, {round(60/blink_interval,1)}bpm / {len(tracked_eye_list)}+{debug_added_nodes} / {round(1/((this_perf_counter-last_perf_counter)/10), 2)}fps ({round(cv_time*1000,2)}/{round(((this_perf_counter-last_perf_counter)*100),2)}ms)', end="        \r")
        last_perf_counter = this_perf_counter
        debug_added_nodes = 0

    # print(end="                                               \r")
    iterator += 1
    cv2.imshow('frame', img)
    # cv2.imshow('Debug Window', grey2)
    k = cv2.waitKey(1) & 0xff
    if k == 27:
        print()
        break
cap.release()
cv2.destroyAllWindows()
