

import time
from adafruit_servokit import ServoKit
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

import threading
import Main

keypadInput = ""
secretCode = "124#"
registerCode = "*888*"
authIDs = [1034121356282]
kit = ServoKit(channels=8)
rfid = SimpleMFRC522()
L1 = 5
L2 = 6
L3 = 13
L4 = 19

C1 = 12
C2 = 16
C3 = 20
C4 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)


GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def keypadCallback(channel):
    global keypadPressed
    if keypadPressed == -1:
        keypadPressed = channel

GPIO.add_event_detect(C1, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C2, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C3, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C4, GPIO.RISING, callback=keypadCallback)

def setAllLines(state):
    GPIO.output(L1, state)
    GPIO.output(L2, state)
    GPIO.output(L3, state)
    GPIO.output(L4, state)

def checkSpecialKeys():
    
    global keypadInput, mainThread2, mainThread1
    pressed = False

    GPIO.output(L3, GPIO.HIGH)

    if (GPIO.input(C4) == 1):
        print("Input reset!")
        pressed = True

    GPIO.output(L3, GPIO.LOW)
    GPIO.output(L1, GPIO.HIGH)

    if (not pressed and GPIO.input(C4) == 1):
        if keypadInput == secretCode:
            print("Welcome")
            servoMotorTask()
        

        elif keypadInput == registerCode:
            mainThread1.pause()
            mainThread2.pause()
            print("Register!")   
            id, text = rfid.read_no_block()
            while id==None:
                print("scan card")
                id, text = rfid.read_no_block()
            
            if id in authIDs:
                print("user already exixsts")
            else:
                authIDs.append(id)
                print("Success!")
            
            mainThread1.resume()
            mainThread2.resume()
        else: 
            print("Invalid code")
            
        pressed = True

    GPIO.output(L3, GPIO.LOW)

    if pressed:
        keypadInput = ""

    return pressed

def readLine(line, characters):
    global keypadInput

    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        keypadInput = keypadInput + characters[0]
    if(GPIO.input(C2) == 1):
        keypadInput = keypadInput + characters[1]
    if(GPIO.input(C3) == 1):
        keypadInput = keypadInput + characters[2]
    if(GPIO.input(C4) == 1):
        keypadInput = keypadInput + characters[3]
    GPIO.output(line, GPIO.LOW)

def keypadTask():

    keypadPressed = -1
    try:
        while True:
            if keypadPressed != -1:
                setAllLines(GPIO.HIGH)
                if GPIO.input(keypadPressed) == 0:
                    keypadPressed = -1
                else:
                    time.sleep(0.1)
            else:
                if not checkSpecialKeys():
                    readLine(L1, ["1","2","3","A"])
                    readLine(L2, ["4","5","6","B"])
                    readLine(L3, ["7","8","9","C"])
                    readLine(L4, ["*","0","#","D"])
                    time.sleep(0.1)
                else:
                    time.sleep(0.1)
        
    except KeyboardInterrupt:
        print("\nApplication stopped!")




def servoMotorTask():
    kit.servo[0].angle = 180
    kit.continuous_servo[1].throttle = 1
    time.sleep(1)
    kit.continuous_servo[1].throttle = -1
    time.sleep(1)
    kit.servo[0].angle = 0
    kit.continuous_servo[1].throttle = 0


def rfidReadTask():
    id, name = rfid.read()
    return id, name



def testId():
    while True:
        id, name = rfidReadTask()
        if id in authIDs:
            greeting = "Welcome " + name.title()
            print(greeting)
            servoMotorTask

        else:
            print("Acess Denied")




mainThread1 = Main(target=testId)
mainThread2 = Main(target=keypadTask)
if __name__ == '__main__':
    try:
        mainThread1.start()
        mainThread2.start()
        mainThread1.join()
        mainThread2.join()

    finally:
        GPIO.cleanup()





