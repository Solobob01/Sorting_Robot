from edge_impulse_linux.image import ImageImpulseRunner
from sendDataToArduino import sendPosToArduino
from useModel import getNumberValue
# Import essential libraries
import requests
import imutils
import cv2
import os
import sys, getopt
import numpy as np
from scipy import ndimage


URL = "http://192.168.1.24:8080/shot.jpg"
#modelfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "model.eim")
FINAL_POS = [(-350, -350), (-100, -350), (400,-250), (400, -50), (400,400),
             (400, -250), (-150, -350), (-200, -150), (-200, -200), (-200, -250)]

BLUE_FINAL_POS = (400, -50)
GREEN_FINAL_POS = (400, 400)                                                                                                                                                        
YELLOW_FINAL_POS = (400, 200)
PURPLE_FINAL_POS = (400, -250)

NUMBER_STRING = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
TOTAL_DETECTIONS = 20
THR = 5

KERNEL = np.array([[0, -1, 0],
                   [-1, 5,-1],
                   [0, -1, 0]])

SCREEN_X = 600
SCREEN_Y = 600

R_MIN = -300
R_MAX = 300

def transformToRobotCoord(x_c, y_c):
    #newX = x_c# - SCREEN_X/2
    #newY = y_c# - SCREEN_Y/2
    #scaleX = -300/155
    #scaleY = 300/552

    #return (round(newX * scaleX) , round(newY * scaleY))
    return (-400, 400)

def findMaxValue(detection):
    maxCount = -1
    maxValue = ''
    for i in detection:
        temp = detection.count(i)
        if temp > maxCount:
            maxCount = temp
            maxValue = i
    if maxCount >= THR:
        return StringToNumber(maxValue)
    return -1

def StringToNumber(value):
    index = 0
    for i in NUMBER_STRING:
        if value == i:
            return index
        index += 1
    return -1

def getImageInput():
    img_resp = requests.get(URL)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    img = cv2.resize(img, (SCREEN_X, SCREEN_Y), interpolation = cv2.INTER_AREA)
    return img
    
    return cv2.flip(img, -1)

def getAllMask(listOfMasks):
    finalMask = listOfMasks[0]
    for i in listOfMasks:
        finalMask = cv2.bitwise_or(finalMask, i)
    return finalMask


def getProperMask(img):
    listOfMasks = []
    hsv = cv2.cvtColor(img , cv2.COLOR_BGR2HSV)
    #blue
    lower_bound_1 = np.array([105, 96, 121])	 
    upper_bound_1 = np.array([153, 255, 255])
    listOfMasks.append(cv2.inRange(hsv, lower_bound_1, upper_bound_1))

    #yellow
    lower_bound_3 = np.array([23, 95, 92])	 
    upper_bound_3 = np.array([44, 154, 247])
    listOfMasks.append(cv2.inRange(hsv, lower_bound_3, upper_bound_3))

    #green
    lower_bound_4 = np.array([44, 101, 68])	 
    upper_bound_4 = np.array([79, 255, 255])
    listOfMasks.append(cv2.inRange(hsv, lower_bound_4, upper_bound_4))

    #purple
    lower_bound_5 = np.array([125, 111, 94]) 
    upper_bound_5 = np.array([147, 193, 156])
    listOfMasks.append(cv2.inRange(hsv, lower_bound_5, upper_bound_5))
    allMask = getAllMask(listOfMasks)
    return allMask

def crop_rect(img, rect):
    # get the parameter of the small rectangle
    center, size, angle = rect[0], rect[1], rect[2]
    center, size = tuple(map(int, center)), tuple(map(int, size))

    # get row and col num in img
    height, width = img.shape[0], img.shape[1]

    # calculate the rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1)
    # rotate the original image
    img_rot = cv2.warpAffine(img, M, (width, height))

    # now rotated rectangle becomes vertical, and we crop it
    img_crop = cv2.getRectSubPix(img_rot, size, center)
    return img_crop, img_rot

def findBiggestContourMask(mask, img):
    contours, h = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggest_contours = (-1, -1, -1, -1)
    maxArea = 50
    rect = None
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if cv2.contourArea(c) >= maxArea:
            biggest_contours = cv2.boundingRect(c)
            maxArea = cv2.contourArea(c)
            rect = cv2.minAreaRect(c)
    x, y, w, h = biggest_contours
    #if x != -1:
        #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
    #cv2.imshow("Image", img)
    return rect  

def findBiggestContourBrick(mask):
    contours, h = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggest_contours = (-1, -1, -1, -1)
    maxArea = 1000
    rect = None
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if x > 200 or y < 200:
                continue
        if cv2.contourArea(c) >= maxArea:
            biggest_contours = cv2.boundingRect(c)
            maxArea = cv2.contourArea(c)
            rect = cv2.minAreaRect(c)
    return rect

def getCroppedBrick(img):
    brick_rect = findBiggestContourBrick(getProperMask(img))
    if np.any(brick_rect is None):
        print("No brick detected")
        return None, (0, 0, 0)
    (x, y), (w, h), angle = brick_rect
    img_crop, img_rot = crop_rect(img, brick_rect)
    if w >= h:
        img_crop = ndimage.rotate(img_crop, 270)
    else:
        img_crop = ndimage.rotate(img_crop, 180)
    return img_crop, (x + w/2, y + h/2, angle)

def getNumberMask(img):
    hsv = cv2.cvtColor(img , cv2.COLOR_BGR2HSV)
    lower_bound_1 = np.array([93, 7, 217])	 
    upper_bound_1 = np.array([125, 94, 255])
    mask = cv2.inRange(hsv, lower_bound_1, upper_bound_1)
    return cv2.GaussianBlur(mask,(5,5),cv2.BORDER_DEFAULT)

def getCroppedNumber(img):
    cropped_brick, (x, y, angle) = getCroppedBrick(img)
    #cv2.imshow("MASk", getNumberMask(cropped_brick))
    if np.any(cropped_brick is None):   
        return None, (0, 0, 0)
    rect = findBiggestContourMask(getNumberMask(cropped_brick), cropped_brick)
    if np.any(rect is None):
        return None, (0, 0, 0)
   
    img_crop, img_rot = crop_rect(cropped_brick, rect)
    return cv2.filter2D(src=img_crop, ddepth=-3, kernel=KERNEL), (x ,y, angle)


def numberSort(arduino):
    detections = list()
    while True:
        img = getImageInput()
        numberDetected = -1
        #cv2.imshow("Android_cam", img)
        cropped_brick, (_, _, _) = getCroppedBrick(img)
        cropped_number, (x, y, angle) = getCroppedNumber(img)
        if np.any(cropped_brick is None) or (x == 0 and y == 0):
            print("Number not detected")
            detections.clear()
            continue
            
        #cv2.imshow("Cropped brick", cropped_brick)
        #cv2.imshow("Cropped number", cropped_number)
        value = getNumberValue(cropped_number)
        print(f'Predicted value: {value}')
        detections.append(value)
        if len(detections) >= TOTAL_DETECTIONS:
            print("Check the value")
            numberDetected = findMaxValue(detections)
            detections.clear()
        if numberDetected != -1:
            print("numberDetected: " + str(numberDetected))
            (newX, newY) = transformToRobotCoord(x, y)
            (x_finish, y_finish) = FINAL_POS[numberDetected]
            sendPosToArduino(newX, newY, angle, x_finish, y_finish, arduino)
            print("Pos: ( " + str(x) + ", " + str(y) + ")")
            print("Pos: ( " + str(newX) + ", " + str(newY) + ")")
        else:
            print("Not enough values in array")
        # Press Esc key to exit
        if cv2.waitKey(1) == 27:
            break
