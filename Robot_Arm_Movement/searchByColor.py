from sendDataToArduino import sendPosToArduino
# Import essential libraries
import requests
import cv2
import numpy as np
import imutils
import time
  
# Replace the below URL with your own. Make sure to add "/shot.jpg" at last.
POSSIBLE_COLOR = ['blue', 'yellow','green', 'purple']


SCREEN_X = 600
SCREEN_Y = 600

BLUE_FINAL_POS = (400, -50)
GREEN_FINAL_POS = (400, 400)                                                                                                                                                        
YELLOW_FINAL_POS = (400, 200)
PURPLE_FINAL_POS = (400, -250)
FINAL_POS = [BLUE_FINAL_POS, YELLOW_FINAL_POS, GREEN_FINAL_POS, PURPLE_FINAL_POS]

R_MIN = -300
R_MAX = 300

URL = "http://130.89.88.113:8080/shot.jpg"
def getImageInput():
    img_resp = requests.get(URL)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    img = cv2.resize(img, (SCREEN_X, SCREEN_Y), interpolation = cv2.INTER_AREA)
    return img

#ecran 208 507
#robot 250 250

#ecran 172 270
#robot 0 350

def transformToRobotCoord(x_c, y_c):
    #newX = x_c# - SCREEN_X/2
    #newY = y_c# - SCREEN_Y/2
    #scaleX = -300/155
    #scaleY = 300/552

    #return (round(newX * scaleX) , round(newY * scaleY))
    return (-400, 400)

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

    return listOfMasks

def findBricks(img):
    allPos = dict.fromkeys(POSSIBLE_COLOR)
    listOfMasks = getProperMask(img)
    index = 0
    rect = None
    for mask in listOfMasks:
        #cv2.imshow(POSSIBLE_COLOR[index], mask)
        contours, h = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        biggest_contours = (-1, -1, -1, -1)
        maxArea = 1000
        for c in contours:
            
            x, y, w, h = cv2.boundingRect(c)
            if x > 200 or y < 200:
                continue
            if cv2.contourArea(c) >= maxArea:
                biggest_contours = cv2.boundingRect(c)
                maxArea = cv2.contourArea(c)
                rect = cv2.minAreaRect(c)
        x, y, w, h = biggest_contours
        if x != -1 and y != -1:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(img=img, text=POSSIBLE_COLOR[index], org=(x, y), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 255, 0),thickness=1)
            cv2.putText(img=img, text=str((round(x + w/2),round(y + h/2))), org=(x, y - 20), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(255, 255, 0),thickness=1)
            cv2.circle(img, (round(x + w/2),round(y + h/2)), radius=2, color=(0, 0, 255), thickness=20)
            (_, _), (_, _), angle = rect
            allPos[POSSIBLE_COLOR[index]] = (round(x + w/2), round(y + h/2), angle)
        index += 1
    return img, allPos

 
def colorSort(arduino, debug):
    time.sleep(1)
    while True:
        img = getImageInput()
        img, allPos = findBricks(img)
        if debug == 'win':
            cv2.imshow("Input", img)
        index = 0
        print(allPos)
        for color in POSSIBLE_COLOR:
            if allPos[color] != None:
                x_start, y_start, angle = allPos[color]
                x_finish, y_finish = FINAL_POS[index]
                print("Color: " + POSSIBLE_COLOR[index])
                print("X_start: " + str(x_start) + " Y_start: " + str(y_start))
                new_x, new_y = transformToRobotCoord(x_start, y_start)
                print("X_new: " + str(new_x) + " Y_new: " + str(new_y))
                if debug == 'linux':
                    sendPosToArduino(new_x, new_y, angle, x_finish, y_finish, arduino)
            index += 1
        # Press Esc key to exit
        if cv2.waitKey(1) == 27:
            break
  
cv2.destroyAllWindows()