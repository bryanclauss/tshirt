import keyboard
import yaml
import RPi.GPIO as GPIO           
from time import sleep

try:
    with open('/srv/fold-count', 'r') as fold_file:
        count = fold_file.read()
        totalCountNum = int( count.strip() )
except:
    totalCountNum = 1
    
with open('/srv/tshirt.yml', 'r') as file:
    tshirt = yaml.load(file, Loader=yaml.FullLoader)
GPIO.setwarnings(False)
GPIO_Mode = tshirt["GPIO_Mode"]
eval( "GPIO.setmode(GPIO.%s)" % (GPIO_Mode)) 

hotkey = tshirt["KeyboardTriggerButton"]
program = tshirt["ProgramNameToRun"]
steps = tshirt[program]

PinNumbers = tshirt["PinNumbers"]
for pinName in PinNumbers:
    pinNumber = PinNumbers[pinName]
    print( "Setting pin # %s to GPIO.OUT" % (pinNumber) )
    GPIO.setup(pinNumber, GPIO.OUT) 


def perform(step, pinNumber, pinState, delay):
    if pinState == "ON" or pinState == True:
        binaryState = int(1)
    else:
        binaryState = int(0)
    seconds = 0.001 * delay
    print("%s: Setting %s to %s, then sleeping %s ms" % (step, pinNumber, pinState, delay))
    GPIO.output(pinNumber, int(binaryState))
    sleep(seconds)

def runProgram(steps):
    for step in steps:
        pinName = steps[step]["PinName"]
        pinNumber = tshirt["PinNumbers"][pinName]
        pinState = steps[step]["PinState"]
        delay = steps[step]["Delay"]
        perform(step, pinNumber, pinState, delay)

def showInstructions(countNum, totalCountNum):
    print(R"""
   __   __
 /|  `-´  |\
/_|  o.o  |_\  Press the %s key to fold a shirt
  | o`o´o |
  |  o^o  |
  |_______|     Total Fold Count: %s    Current Count: %s

    """ % (hotkey, totalCountNum, countNum)
    )

countNum = 1
showInstructions(countNum, totalCountNum)

def updateCountFile(totalCountNum):
    with open('/srv/fold-count', 'w') as fold_file:
        fold_file.write( str(totalCountNum) )
        fold_file.close()

try:
    while True:
        if keyboard.is_pressed(hotkey):
            print("%s pressed, folding now..." % (hotkey))
            runProgram(steps)
            showInstructions(countNum, totalCountNum)
            sleep(.1)
            print("Finished fold #%s <- since last restart" % (countNum))
            countNum += 1
            totalCountNum += 1
            updateCountFile(totalCountNum)
        sleep(.1)
except KeyboardInterrupt:
    GPIO.cleanup()
