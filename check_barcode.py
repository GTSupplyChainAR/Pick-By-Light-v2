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
import logging
import os
import utils
from models import PickingTask


# Setup logging
logger = logging.getLogger(os.path.basename(__file__))
logger = utils.configure_logger(logger)


carts = ["C11", "C12", "C13"]


def get_barcode_from_input():
    barcode = input("Barcode: ")[4:]
    return barcode


def play_error_sound():
    print("\a")  # only checked on macOS


def compareBarcode(pickpaths):
    """Function that runs a full task with a set of carts and a list of pickpaths.

    Args:
        cartSet (list): list of carts in a task, ordered
    """
    for pickorder in pickpaths:  # type: PickingTask
        logger.info("TASK START: %s" % pickorder)

        expected_source_bins = set([bin.tag for bin in pickorder.source_bins])
        logger.debug('\tExpecting source bins to be scanned: %s' % list(expected_source_bins))

        # Wait for all source bins to be scanned
        while expected_source_bins:
            barcode = get_barcode_from_input()
            if barcode not in expected_source_bins:
                logger.warning('\t\tUnexpected barcode: %s' % barcode)
                play_error_sound()
            else:
                logger.info('\t\tCorrect source bin barcode scanned: %s' % barcode)
                expected_source_bins.remove(barcode)

        # Wait for receive bin to be scanned
        receive_bin_scanned = False
        while not receive_bin_scanned:
            barcode = get_barcode_from_input()
            if barcode != pickorder.receive_bin.tag:
                logger.info('\t\tUnexpected barcode: %s' % barcode)
                play_error_sound()
            else:
                logger.info('\t\tCorrect receive bin barcode scanned: %s' % barcode)
                receive_bin_scanned = True

        logger.info("TASK END: %s" % pickorder)


def main():
    pickpaths = utils.get_pick_paths_from_user_choice()
    compareBarcode(pickpaths)


if __name__ == "__main__":
    import sys
    try:
        main()
    except Exception as exception:
        print("Experiment Failed.")
        print(exception)
    finally:
        print("\nExperiment Complete.")
