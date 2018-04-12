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
import re
import copy
from socket import *
import logging
from models import PickingTask
import utils

# Setup logging
logger = logging.getLogger(os.path.basename(__file__))
logger = utils.configure_logger(logger)

carts = ["C11", "C12", "C13"]

# Pickpath to test displays
pp = {"A11": 88, "A12": 88, "A13": 88, "A21": 88, "A22": 88, "A23": 88, "A31": 88, "A32": 88, "A33": 88, "A41": 88,
      "A42": 88, "A43": 88, "B11": 88, "B12": 88, "B13": 88, "B21": 88, "B22": 88, "B23": 88, "B31": 88, "B32": 88,
      "B33": 88, "B41": 88, "B42": 88, "B43": 88}

rightdisplay = {'0': 63, '1': 6, '2': 91, '3': 79, '4': 102, '5': 109, '6': 125, '7': 7, '8': 127, '9': 111}
leftdisplay = {'0': 16128, '1': 1536, '2': 23296, '3': 20224, '4': 26112, '5': 27904, '6': 32000, '7': 1792, '8': 32512,
               '9': 28416}

PICK_BY_LIGHT_RACK_ADDRESS = ('192.168.2.255', 3865)

RECEIVE_BIN_INITIAL_LIGHT_LAYOUT = 47375

EMPTY_LIGHT_LAYOUT = 0

BOTH_DECIMAL_POINTS_LIGHT_LAYOUT = 32896

sockhub = socket(AF_INET, SOCK_DGRAM)
sockhub.bind(('', 3865))
sockhub.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)


def ChangeDisplay(sockcntrl, display, number):
    """Function that changes a particular display to show a number.

    Args:
        sockcntrl (obj): socket connection
        display (str): id of display
        number (int): number to show on display
    """
    message1 = 'xpl-cmnd\n{\nhop=1\nsource=bnz-sender.orderpick\ntarget=smgpoe-lamp.'
    message2 = '\n}\ncontrol.basic\n{\ndevice=display\ntype=variable\ncurrent='
    message3 = '\n}\n'
    message = message1 + display + message2 + str(number) + message3
    message = message.encode('utf-8')
    return sockcntrl.sendto(message, PICK_BY_LIGHT_RACK_ADDRESS)


def NumberConvert(number):
    """Function that converts input to representation for display.

    Args:
        number (int): number before conversion
        setup (boolean): ???
    """
    onesdigit = number % 10
    number //= 10
    tensdigit = number % 10

    if tensdigit == 0:
        return rightdisplay[str(onesdigit)]
    else:
        return leftdisplay[str(tensdigit)] + rightdisplay[str(onesdigit)]


def reset():
    """Function that resets all displays.
    """
    ChangeDisplay(sockhub, '*', EMPTY_LIGHT_LAYOUT)


def initReceive(receiveDisplay):
    """Function which starts the order on the receive bin.

    Args:
        receiveDisplay (str): id of display corresponding to receive bin
    """
    ChangeDisplay(sockhub, receiveDisplay, RECEIVE_BIN_INITIAL_LIGHT_LAYOUT)


def press():
    """Function which checks if button is pushed and returns button.

    Returns:
        display (str): id of display corresponding to button pressed
    """
    data, address = sockhub.recvfrom(4096)
    # Ignore heartbeats
    if data and "hbeat".encode("utf-8") not in data:
        if ("HIGH".encode('utf-8') in data):
            display = re.findall('[ABC]\d{2}'.encode("utf-8"), data)[0].decode()

            return display


def initDisplays(pickpath):
    """Function which starts the order on the displays.

    Args:
        pickpath (dict): keys are displays and values are quantities
    """
    for display, quantity in pickpath.items():
        ChangeDisplay(sockhub, display, NumberConvert(quantity))


def runTask(pickpaths):
    """Function that runs a full task with a set of carts and a list of pickpaths.

    Args:
        cartSet (list): list of carts in a task, ordered
    """
    for pickorder in pickpaths:  # type: PickingTask

        initReceive(pickorder.receive_bin.tag)
        orderInProgress = False

        while not orderInProgress:
            if press() == pickorder.receive_bin.tag:
                logger.info("TASK START: %s" % pickorder)

                runPickPath(pickorder)
                reset()
                orderInProgress = True


def runPickPath(pickpath):  # type: (PickingTask) -> None
    """Function that runs a full pick path.

    Args:
        pickpath (dict): keys are displays and values are quantities
    """
    initDisplays(pickpath.for_init_displays)

    # Control loop will run while the pickpath is in progress
    pickpath_completed = False

    remaining_source_bin_tags_and_counts = copy.deepcopy(pickpath.source_bins_in_dict)  # type: dict
    receive_bin_tag = pickpath.receive_bin.tag

    while not pickpath_completed:
        # Wait for a button to be pressed...
        pressed_bin_tag = press()

        # Ignore bad packets
        if pressed_bin_tag is None:
            continue

        logger.debug("Subject pressed %s." % pressed_bin_tag)

        # If the subject pressed all of the required source bins' buttons and now wants to end the task
        if not remaining_source_bin_tags_and_counts and pressed_bin_tag == receive_bin_tag:
            # Set the receive bin tags to 0
            ChangeDisplay(sockhub, receive_bin_tag, NumberConvert(0))

            pickpath_completed = True
            logger.info("TASK END: %s" % pickpath)

        # Else if the subject pressed a source bin
        elif pressed_bin_tag in remaining_source_bin_tags_and_counts:
            # Set the pressed source bin value to 0
            ChangeDisplay(sockhub, pressed_bin_tag, NumberConvert(0))

            # Subject has pressed the source bin and doesn't have to do so again.
            # Remove this bin from the expected/remaining ones.
            pressed_source_bin_count = remaining_source_bin_tags_and_counts.pop(pressed_bin_tag)  # type: int

            # Recompute total to display on receive bin
            new_receive_bin_total = sum(remaining_source_bin_tags_and_counts.values())

            logger.debug("%s with %d items was pressed. Decrementing total to %d" %
                         (pressed_bin_tag, pressed_source_bin_count, new_receive_bin_total))

            # Update the total on the receive bin
            ChangeDisplay(sockhub, receive_bin_tag, NumberConvert(new_receive_bin_total))

        else:
            logger.warning("Unexpected button pressed: %s" % pressed_bin_tag)


def main():
    reset()
    pickpaths = utils.get_pick_paths_from_user_choice()
    runTask(pickpaths)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ki:
        print("Handling keyboard interrupt. Resetting displays")
        reset()
    except Exception as exception:
        print("Experiment Failed.")
        print(exception)
    finally:
        print("\nExperiment Complete.")
        sockhub.close()
