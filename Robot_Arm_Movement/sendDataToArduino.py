import serial
import time


def sendPosToArduino(x_start, y_start, angle, x_finish, y_finish, arduino):
    output = str(x_start) + " " + str(y_start) + " " + str(round(90 - angle)) +  " " +  str(x_finish) + " " + str(y_finish) + "\n"
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
