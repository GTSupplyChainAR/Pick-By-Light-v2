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
import os
import time
import copy
from socket import *
import logging
from models import PickingTask
import utils
from constants import EMPTY_LIGHT_LAYOUT, ALL_DISPLAYS
from visualize import BLANK_DISPLAY

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

BOTH_DECIMAL_POINTS_LIGHT_LAYOUT = 32896

sockhub = socket(AF_INET, SOCK_DGRAM)
sockhub.bind(('', 3865))
sockhub.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)


def ChangeDisplay(display=None, all_displays=False, number=None, layout=None):
    """Function that changes a particular display to show a number.

    Args:
        sockhub (obj): socket connection
        display (str): id of display
        number (int): number to show on display
        layout (int): a layout to display without running number conversion
    """

    assert (number is not None or layout is not None) and not (number is not None and layout is not None)

    if all_displays:
        display = ALL_DISPLAYS

    global visualizer
    if layout is not None:
        viz_value = layout
    else:
        viz_value = number
    visualizer.change_display(display, viz_value)

    if layout is not None:
        rack_value = layout
    else:
        rack_value = NumberConvert(number)

    message1 = 'xpl-cmnd\n{\nhop=1\nsource=bnz-sender.orderpick\ntarget=smgpoe-lamp.'
    message2 = '\n}\ncontrol.basic\n{\ndevice=display\ntype=variable\ncurrent='
    message3 = '\n}\n'
    message = message1 + display + message2 + str(rack_value) + message3
    message = message.encode('utf-8')
    response = sockhub.sendto(message, PICK_BY_LIGHT_RACK_ADDRESS)

    # HACK: Get rid of this delay! It's confusing!
    # time.sleep(0.05)

    return response


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
    ChangeDisplay(all_displays=True, layout=EMPTY_LIGHT_LAYOUT)


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
        logger.debug('Setting display %s = %d' % (display, quantity))
        ChangeDisplay(display=display, number=quantity)


def run_all_pick_tasks(pick_tasks):
    """Function that runs a full task with a set of carts and a list of pickpaths.

    Args:
        cartSet (list): list of carts in a task, ordered
    """

    for i, pick_task in enumerate(pick_tasks):  # type: PickingTask

        # Show start symbol to subject on first task
        if i == 0:
            ChangeDisplay(display=pick_task.receive_bin.tag, layout=RECEIVE_BIN_INITIAL_LIGHT_LAYOUT)

            # Get user's confirmation to start first task (must press first receive bin to start)
            first_task_started = False
            while not first_task_started:
                if press() == pick_task.receive_bin.tag:
                    first_task_started = True

        logger.info("TASK START: %s" % pick_task)

        runPickPath(pick_task)

        logger.info("TASK END: %s" % pick_task)

        reset()

        time.sleep(0.1)


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

    correctly_pressed_source_bins = list()

    while not pickpath_completed:
        # Wait for a button to be pressed...
        pressed_bin_tag = press()

        # Ignore bad packets
        if pressed_bin_tag is None:
            continue

        logger.debug("Subject pressed %s." % pressed_bin_tag)

        # Else if the subject pressed a source bin
        if pressed_bin_tag in remaining_source_bin_tags_and_counts:
            # Set the pressed source bin value to 0
            ChangeDisplay(display=pressed_bin_tag, number=0)

            # Subject has pressed the source bin and doesn't have to do so again.
            # Remove this bin from the expected/remaining ones.
            correctly_pressed_source_bins.append(pressed_bin_tag)
            pressed_source_bin_count = remaining_source_bin_tags_and_counts.pop(pressed_bin_tag)  # type: int

            # Recompute total to display on receive bin
            new_receive_bin_total = sum(remaining_source_bin_tags_and_counts.values())

            logger.debug("%s with %d items was pressed. Decrementing total to %d" %
                         (pressed_bin_tag, pressed_source_bin_count, new_receive_bin_total))

            # Update the total on the receive bin
            ChangeDisplay(display=receive_bin_tag, number=new_receive_bin_total)

        # If the subject pressed all of the required source bins' buttons the task is now over
        elif not remaining_source_bin_tags_and_counts and pressed_bin_tag == receive_bin_tag:
            # Set the receive bin tags to empty (pick path is done)
            for tag in correctly_pressed_source_bins + [receive_bin_tag]:
                logger.debug("Clearing display %s" % tag)
                ChangeDisplay(display=tag, layout=EMPTY_LIGHT_LAYOUT)

            pickpath_completed = True

        else:
            logger.warning("Unexpected button pressed: %s" % pressed_bin_tag)


def main():
    reset()
    pickpaths = utils.get_pick_paths_from_user_choice()

    log_filename = input("What file do you want to write to? ")
    utils.configure_file_logger(logger, log_filename)

    run_all_pick_tasks(pickpaths)


if __name__ == "__main__":
    try:
        from visualize import LightRackVisualizer

        global visualizer
        visualizer = LightRackVisualizer()

        visualizer.run(main)

    except KeyboardInterrupt as ki:
        print("Handling keyboard interrupt. Resetting displays")
    except Exception as exception:
        print("Experiment Failed.")
        print(exception)
    finally:
        print("\nExperiment Complete.")
        reset()
        sockhub.close()
