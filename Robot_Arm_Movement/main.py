#from searchByNumber import numberSort
from searchByColor import colorSort
from searchByNumber import numberSort
import sys, getopt
import serial
import time

def getArguments(argv):
    sortMode = ''
    debugMode = ''
    opts, args = getopt.getopt(argv,"hm:c:",["mode=", "debug="])
    for opt, arg in opts:
        if opt == '-h':
            print ('python ./test.py -m {color, number} -c {none, red, green, blue, yellow, purple}')
            sys.exit()
        elif opt in ("-m", "--mode"):
            sortMode = arg
        elif opt in ("-d", "--debug"):
            debug = arg
    return sortMode, debug

def sendWaveToArduino(arduino):
    output = "wave \n"
    print("Writting: " + output)
    arduino.write(output.encode('utf-8'))
    while True:
        response = arduino.readline().decode('utf-8')
        if 'DONE\n' in response:
            print("The code is done")
            break
        elif 'ERROR_DOWN\n' in response:
            print("There is no solution to this coord on drop")
            break
        elif 'ERROR_UP\n' in response:
            print("There is no solution to this coord on pick up")
            break
        #print("response: " + response)
        time.sleep(0.5)


def callRightFunction(sortMode, debug, arduino):
    if sortMode == 'color' :
        colorSort(arduino, debug)
    elif sortMode == 'number' :
        numberSort(arduino)
    elif sortMode == 'wave':
        sendWaveToArduino(arduino)
    #else:
        #print("INCORECT MODE")

def main(argv):
    (sortMode, debug) = getArguments(argv)
    if debug == 'linux':
        arduino = serial.Serial(port = '/dev/ttyS9',baudrate = 9600, timeout=0)
        time.sleep(2)
    elif debug == 'win':
        arduino = ''
    callRightFunction(sortMode,debug, arduino)
    if debug == 'linux':
        arduino.close()

if __name__ == "__main__":
    time.sleep(2)
    main(sys.argv[1:])
    
