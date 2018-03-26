"""check_barcode.py

This modules works as part of the paper system at the Georgia Tech
Contextual Computing Group's dense pick setup located in TSRB Lab 243. Run with 
a json file, usually called pick_tasks.json
    $ python check_barcode.py pick_tasks.json

Todo:
    * Write log file according to Theo's example
    * Do time stamps
    * Fix docstrings (esp ChangeDisplay)
    * Change recvfrom to recv in receivePackets func
"""
import json
import copy

pickpath = {}
taskIndex, orderIndex = 0,0

carts = ["C11", "C12", "C13"]
racks = ["A", "B"]

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

def jsonInputHandler(filename):
    """Take json file containing tasks which contain orders and return dictionaries
    {
        "tasks": [
            {
                "orders": [
                    {
                        "A32": 1,
                        "B31": 2,
                        "target": "C11"
                    },
                    {
                        "A41": 3,
                        "target": "C12"
                    }
                ]
            }
        ]
    }

    Keyword arguments:
    filename - name of json file

    Returns:
    returnList - nested list of separate orders
    """
    fileh = open(filename)
    data = json.load(fileh)
    fileh.close()
    tasks = data['tasks']
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

def compareBarcode(checkList):
    """Take a list of order lists and iterate through to check if barcodes match orders. If not, beep on laptop

    Keyword arguments:
    checkList - nested list of separate orders

    Returns:
    None
    """
    for task in checkList:
        for order in task:
            print(order)
            while list(order) != []:
                barcode = input("Barcode: ")[4:]
                if barcode not in order:
                    print("\a")
                else:
                    order.pop(barcode)

def main(args):
    checkList = jsonInputHandler(args)
    compareBarcode(checkList)

if __name__ == "__main__":
    import sys
    try:
        main(sys.argv[1])
    except Exception as exception:
        print("Experiment Failed.")
        print(exception)
    except:
        print("\nExperiment Complete.")