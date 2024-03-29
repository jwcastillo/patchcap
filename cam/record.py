#!/usr/bin/env python
import cv2
import sys

if len(sys.argv)!=2:
    uri = "rtsp://root:root@192.168.3.20:554/cam1/onvif-h264"
    output = "out.avi"
else:
    uri = sys.argv[1]
    output = sys.argv[2]


video = cv2.VideoCapture(uri)
w = (int)(video.get( cv2.CAP_PROP_FRAME_WIDTH ))
h = (int)(video.get( cv2.CAP_PROP_FRAME_HEIGHT ))
_fps = video.get(cv2.CAP_PROP_FPS)
if not _fps: _fps = 25 
writer = cv2.VideoWriter(filename="out.avi",  
                         fourcc=cv.CV_FOURCC('X','2', '6', '4'), 
                         fps = _fps,
                         frameSize=(w, h))

cv2.namedWindow("Camera")
while True:
    flag, frame = video.read()
    if not flag: continue
    cv2.imshow("Camera", frame)
    key_pressed = cv2.waitKey(10)
    if key_pressed == 27:                           #Escape key
        break
    writer.write(frame)

writer.release()
video.release()
