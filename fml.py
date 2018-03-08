"""fml.py

This modules works as part of the Pick By Light system at the Georgia Tech
Contextual Computing Group's dense pick setup located in TSRB Lab 243. 
    $ python fml.py [*args]

Todo:
    * Fix docstrings (esp ChangeDisplay)
    * Change recvfrom to recv in receivePackets func
"""
import json
import re
from time import sleep, time
from socket import *

pickpath = {}
i,j,k = 0,0,0

carts = ["C11", "C12", "C13"]

rightdisplay={'0':63,'1':6,'2':91,'3':79,'4':102,'5':109,'6':125,'7':7,'8':127,'9':111}
leftdisplay={'0':16128,'1':1536,'2':23296,'3':20224,'4':26112,'5':27904,'6':32000,'7':1792,'8':32512,'9':28416}

sockhub = socket(AF_INET, SOCK_DGRAM)
sockhub.bind(('', 3865))
sockhub.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

def readJsonFile(filename):
    """Function which reads json file.

    Args:
        filename (str): name of json file parsed; use format for json 
        specified here: https://goo.gl/Qs4dio

    Returns:
        data (dict): json data as python dictionary
    """
    fileh = open(filename)
    data = json.load(fileh)
    fileh.close()
    return data

def ChangeDisplay(sockcntrl,display,number,setup):
    """Function that changes the display

    Args:
        sockcntrl (obj): socket connection
        display (str): id of display
        number (int): number to show on display
        setup (boolean): ???
    """
    message1='xpl-cmnd\n{\nhop=1\nsource=bnz-sender.orderpick\ntarget=smgpoe-lamp.'
    message2='\n}\ncontrol.basic\n{\ndevice=display\ntype=variable\ncurrent='
    message3='\n}\n'
    message = message1+display+message2+str(number)+message3
    message = message.encode('utf-8')
    return sockcntrl.sendto(message,('192.168.2.255',3865))

def NumberConvert(number, setup=True):
    """Function that converts input to representation for display

    Args:
        number (int): number before conversion
        setup (boolean): ???
    """
    onesdigit = number % 10
    number //= 10
    tensdigit = number % 10
    if (onesdigit == 0 and tensdigit == 0):
        if setup:
            return 0
        else:
            return 32896 # this actually displays decimal points on each display
    if (tensdigit == 0):
        return rightdisplay[str(onesdigit)]
    else:
        return leftdisplay[str(tensdigit)]+rightdisplay[str(onesdigit)]

def reset():
    """Function that resets all displays.
    """
    dispNum = NumberConvert(0, True)
    ChangeDisplay(sockhub, '*', dispNum, False)

def initReceive(receiveDisplay):
    """Function which starts the order on the receive bin.

    Args:
        receiveDisplay (str): id of display corresponding to receive bin
    """
    ChangeDisplay(sockhub, receiveDisplay, 47375, False)

def press():
    """Function which checks if button is pushed and returns button

    Returns:
        display (str): id of display corresponding to button pressed
    """
    data, address = sockhub.recvfrom(4096)
    if data and "hbeat".encode("utf-8") not in data:
        if ("HIGH".encode('utf-8') in data):
            display = re.findall('[ABC]\d{2}'.encode("utf-8"),data)[0].decode()

            return display

def displayCountReceive(receiveDisplay, previousTotal):
    """Function which decrements count left to pick on receive bin

    Args:
        receiveDisplay (str): id of display corresponding to receive bin
        previousTotal (int): int representing the value we decrement from
    """
    pass

def parseExperimentDictionary(experimentData):
    """Function which parses dictionary with experiment data from json file

    Args:
        experimentData (dict): dictionary of structured experiment data 
    """
    tasks = experimentData['tasks']
    global i, j, k
    while i < len(tasks):  
        orders = tasks[i]['orders']
        taskId = tasks[i]['taskId']
        isTrainingTask = tasks[i]['isTrainingTask']
        i += 1

        while j < len(orders):
            sourceBins = orders[j]['sourceBins']

            orderId = orders[j]['orderId']
            receiveBins = orders[j]['receivingBinTag']
            j += 1

            k = 0
            pickpath = {}

            while k < len(sourceBins):
                binTag = sourceBins[k]['binTag']
                numItems = sourceBins[k]['numItems']

                pickpath[binTag] = numItems
                k += 1

            runPickPath(pickpath)


def runExperiment():
    """
    """
    pass

def runTask(cartSet):
    """Function that runs a full task with a set of carts

    Args:
        cartSet (list): list of carts in a task, ordered
    """
    for cart in cartSet:
        initReceive(cart)
        
        while True: #always checking for signals
            if press() == cart:
                taskStartTime = time.time()
                runPickPath(pickpath)
                ChangeDisplay(sockhub, cart, NumberConvert(5), False) #change to TOTAL!

def runPickPath(pickpath):
    """Function that runs a full pick path

    Args:
        pickpath (dict): keys are displays and values are quantities
    """
    reset()

    for k, v in pickpath.items():
        ChangeDisplay(sockhub, k, NumberConvert(v), False)
        sleep(0.15)

    while True:
        display = press()
        if display in pickpath.keys():
            ChangeDisplay(sockhub, display, 63, False)


def main(args): 
    data = readJsonFile(args)
    parseExperimentDictionary(data)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])