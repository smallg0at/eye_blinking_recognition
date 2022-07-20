import numpy as np
import cv2
import math

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')

image_height = 0

class tracked_eye:
    def __init__(self, cx, cy):
        self.age = 0
        self.dead_ticks = 0
        self.referenced = 0
        self.cx = cx
        self.cy = cy

    def __str__(self):
        return f'[{self.cx} {self.cy}]'

    def update(self,x,y,w,h):
        if math.sqrt(pow(self.cx-(x+w/2),2) + pow(self.cy-(y+h/2), 2)) < 100:
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

#number signifies camera
cap = cv2.VideoCapture(0)

while 1:
    ret, img = cap.read()
    image_height = img.shape[0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        if x == 0 or y == 0 or w == 0 or h == 0:
            continue
        
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
        # print(f'{len(faces)} faces ({faces}), {len(eyes)} eyes ({eyes})', end='                                              \r')
        for (ex,ey,ew,eh) in eyes:
            if ex == 0 or ey == 0 or ey == 0 or w == 0 or h == 0:
                continue
            
            ex = int(ex)
            ey = int(ey)
            ew = int(ew)
            eh = int(eh)

            cv2.rectangle(img,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
            if(len(tracked_eye_list)<=0):
                tracked_eye_list.append(tracked_eye(ex+ew/2, ey+eh/2))
            else: 
                activated_count = 0
                for eye_entity in tracked_eye_list:
                    code = eye_entity.update(ex, ey, ew, eh)
                    if code == 1: 
                        activated_count += 1
                        break
                if activated_count == 0:
                    tracked_eye_list.append(tracked_eye(ex+ew/2, ey+eh/2))
        
        for eye_entity in tracked_eye_list:
            if eye_entity.referenced <= 0:
                eye_entity.no_reference_warning()
            if eye_entity.dead_ticks > 10:
                tracked_eye_list.remove(eye_entity)
                continue
            cv2.circle(img,(int(eye_entity.cx), int(eye_entity.cy)),12,(255,0,0),2)
            eye_entity.reset()
            print(f'[{eye_entity.cx} {eye_entity.cy}]', end=' / ')
        print(end="                                               \r")
    cv2.imshow('img',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()