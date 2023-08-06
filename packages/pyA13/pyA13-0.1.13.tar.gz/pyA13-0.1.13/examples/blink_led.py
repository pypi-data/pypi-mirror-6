from time import sleep
from A13_GPIO import *

#initialize module
init()

#set pin as output
if getcfg(PIN2_10) == INPUT:
    setcfg(PIN2_10, OUTPUT)

while True:
    sleep(0.5)
    output(PIN2_10, HIGH)
    sleep(0.5)
    output(PIN2_10, LOW)
    
