"""fml.py

This modules works as part of the Pick By Light system at the Georgia Tech
Contextual Computing Group's dense pick setup located in TSRB Lab 243. Run with 
a json file, usually called pick_tasks.json
    $ python fml.py pick_tasks.json

Todo:
    * Write log file according to Theo's example
    * Do time stamps
    * Fix docstrings (esp ChangeDisplay)
    * Change recvfrom to recv in receivePackets func
"""
import json
import re
import copy
from time import sleep, time
from socket import *

pickpath = {}
taskIndex, orderIndex = 0,0

carts = ["C11", "C12", "C13"]
racks = ["A", "B"]

# Pickpath to test displays
pp = {"A11": 88, "A12": 88, "A13": 88, "A21": 88, "A22": 88, "A23": 88, "A31": 88, "A32": 88, "A33": 88, "A41": 88, 
"A42": 88, "A43": 88, "B11": 88, "B12": 88, "B13": 88, "B21": 88, "B22": 88, "B23": 88, "B31": 88, "B32": 88, 
"B33": 88, "B41": 88, "B42": 88, "B43": 88}

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

def ChangeDisplay(sockcntrl,display,number, setup=False):
    """Function that changes a particular display to show a number.

    Args:
        sockcntrl (obj): socket connection
        display (str): id of display
        number (int): number to show on display
    """
    message1='xpl-cmnd\n{\nhop=1\nsource=bnz-sender.orderpick\ntarget=smgpoe-lamp.'
    message2='\n}\ncontrol.basic\n{\ndevice=display\ntype=variable\ncurrent='
    message3='\n}\n'
    message = message1+display+message2+str(number)+message3
    message = message.encode('utf-8')
    return sockcntrl.sendto(message,('192.168.2.255',3865))

def NumberConvert(number, setup=True):
    """Function that converts input to representation for display.

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
    """Function which checks if button is pushed and returns button.

    Returns:
        display (str): id of display corresponding to button pressed
    """
    data, address = sockhub.recvfrom(4096)
    if data and "hbeat".encode("utf-8") not in data:
        if ("HIGH".encode('utf-8') in data):
            display = re.findall('[ABC]\d{2}'.encode("utf-8"),data)[0].decode()

            return display

def displayCountReceive(receiveDisplay, previousTotal):
    """Function which decrements count left to pick on receive bin.

    Args:
        receiveDisplay (str): id of display corresponding to receive bin
        previousTotal (int): int representing the value we decrement from
    """
    pass

def parseExperimentDictionary(experimentData):
    """Function which parses dictionary with experiment data from json file.

    Args:
        experimentData (dict): dictionary of structured experiment data 
    """
    tasks = experimentData['tasks']
    global taskIndex, orderIndex
    tasksReturn = []
    while taskIndex < len(tasks):  
        orders = tasks[taskIndex]['orders']
        taskId = tasks[taskIndex]['taskId']
        
        taskIndex += 1
        orderIndex = 0

        pick_paths = []
        while orderIndex < len(orders):
            sourceBins = orders[orderIndex]['sourceBins']

            orderId = orders[orderIndex]['orderId']
            receiveBin = orders[orderIndex]['receivingBinTag']
            
            orderIndex += 1
            
            rack_orders = {} 
            for rack in racks: 
                pickpath = {}
                    
                cartTotal = 0
                for source_bin in sourceBins:
                    if source_bin['binTag'][0] == rack:
                        pickpath[source_bin['binTag']] = source_bin['numItems']
                        cartTotal += source_bin['numItems']

                if pickpath != {}:
                    pickpath[receiveBin] = cartTotal
                    cloned_pick_path = copy.deepcopy(pickpath)
                    rack_orders[rack] = cloned_pick_path

            cloned_racks = copy.deepcopy(rack_orders)
            pick_paths.append(cloned_racks)

        ordered_pick_paths = changePickPathOrder(pick_paths)
        cloned_pick_paths = copy.deepcopy(ordered_pick_paths)
        tasksReturn.append(cloned_pick_paths)
    return tasksReturn

def changePickPathOrder(pick_paths):
    """From originally parsed pickpaths from json file, change order to put all orders together
    based on what rack they're from. Return an ordered list.
    """
    ordered_pick_paths = []
    for rack in racks:
        for pp in pick_paths:
            if rack in pp.keys():
                ordered_pick_paths.append(pp[rack])

    return ordered_pick_paths

def initDisplays(pickpath):
    """Function which starts the order on the displays.

    Args:
        pickpath (dict): keys are displays and values are quantities
    """
    for display, quantity in pickpath.items():
        ChangeDisplay(sockhub, display, NumberConvert(quantity), False)
        sleep(0.15)

def runExperiment():
    """
    """
    

def runTask(pickpaths):
    """Function that runs a full task with a set of carts and a list of pickpaths.

    Args:
        cartSet (list): list of carts in a task, ordered
    """
    for picktask in pickpaths:
        print("\n\nTASK START")
        
        for pickorder in picktask:
            initReceive(list(pickorder)[-1])
            orderInProgress = False
            
            while not orderInProgress:
                if press() == list(pickorder)[-1]:
                    runPickPath(pickorder)
                    reset()
                    orderInProgress = True

def runPickPath(pickpath):
    """Function that runs a full pick path.

    Args:
        pickpath (dict): keys are displays and values are quantities
    """
    initDisplays(pickpath)

    pressed = []
    pickpathInProgress = True
    total = pickpath[list(pickpath.keys())[-1]]
    while pickpathInProgress:
        display = press()
        if display != None:
            pressed.append(display)

        correctPressed = set(filter(lambda x: x in pickpath.keys(), pressed))
        displaySet = set(list(pickpath.keys())[:-1])
        receiveBin = list(pickpath.keys())[-1]

        if (displaySet <= correctPressed):
            ChangeDisplay(sockhub, display, 63, False)
            ChangeDisplay(sockhub, receiveBin, 63, False)
            subtaskInProgress = True

            while subtaskInProgress:
                if press() == receiveBin:
                    ChangeDisplay(sockhub, receiveBin, 0, False)
                    subtaskInProgress = False

            pickpathInProgress = False

        elif display in list(pickpath.keys())[:-1]:
            ChangeDisplay(sockhub, display, 63, False)
            total = total - pickpath[display]
            ChangeDisplay(sockhub, receiveBin, NumberConvert(total), False)


def main(args): 
    reset()
    data = readJsonFile(args)
    pickpaths = parseExperimentDictionary(data)
    runTask(pickpaths)

if __name__ == "__main__":
    import sys
    try:
        main(sys.argv[1])
    except Exception as exception:
        print("Experiment Failed.")
        print(exception)
    except:
        print("\nExperiment Complete.")
