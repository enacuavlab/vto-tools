#!/usr/bin/env python3

import cv2
import numpy as np
import os
import glob

CHECKERBOARD = (6,9)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objpoints = []
imgpoints = [] 

objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
prev_img_shape = None

images = glob.glob('./images/*.jpg')
for fname in images:
  print(fname)
  img = cv2.imread(fname)
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  print("Find the chess board corners\n")
  ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
  if ret == True:
    objpoints.append(objp)
    print("Refining pixel coordinates for given 2d points \n");
    corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
    imgpoints.append(corners2)
    
print("Performing camera calibration\n");
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

cv_file = cv2.FileStorage("test.xml", cv2.FILE_STORAGE_WRITE)
cv_file.write("matrix", mtx)
cv_file.write("dist", dist)
cv_file.release()

print("Camera matrix : \n")
print(mtx)
print("dist : \n")
print(dist)
print("rvecs : \n")
print(rvecs)
print("tvecs : \n")
print(tvecs)


