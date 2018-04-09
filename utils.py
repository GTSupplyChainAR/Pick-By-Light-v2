import json
import os
import logging
from models import SourceBin, PickingTask, ReceiveBin
from constants import RACKS


def get_pick_paths_from_user_choice():
    """ Allows a user to select pick paths and then parses the selected JSON file. """
    selected_filename = choose_pick_path_file()
    data = readJsonFile(selected_filename)
    pickpaths = parseExperimentDictionary(data)
    return pickpaths


def choose_pick_path_file():
    """ Interacts with the console so the user can select a pick path to run. """
    study_folders_path = os.path.join('.', 'RFID-Study-Task-Generation', 'output')

    file_number_to_file = {}
    i = 1
    print('Choose from the files below:')

    # Iterate through all folders and pick path files
    for folder_name in os.listdir(study_folders_path):
        folder_path = os.path.join(study_folders_path, folder_name)
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            # Display the option
            print('%-3d %s' % (i, file_name))

            # Register the file path for the printed file name
            file_number_to_file[i] = file_path

            i += 1

    print()  # newline

    print('What file would you like to select?')
    file_id = int(input('> (#) '))

    # Look up the file path by the file_id and return
    file_path_selected = file_number_to_file[file_id]

    print()  # newline

    print('Is this the file you selected?')
    print(file_path_selected)
    confirmation = input('> (y/n) ')

    if confirmation != 'y':
        raise SystemExit('Incorrect file selected.')

    return file_path_selected


def configure_logger(logger, level=logging.DEBUG):
    """ Configures the given logger to print messages at the given level. """
    logger.setLevel(level)
    loggerHandler = logging.StreamHandler()
    loggerFormatter = logging.Formatter('%(asctime)-20s : %(name)-14s : %(levelname)-8s : %(message)s')
    loggerHandler.setFormatter(loggerFormatter)
    loggerHandler.setLevel(level)
    logger.addHandler(loggerHandler)
    return logger


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


def parseExperimentDictionary(experimentData):
    """Function which parses dictionary with experiment data from json file.

    Args:
        experimentData (dict): dictionary of structured experiment data
    """
    tasks = experimentData['tasks']
    taskIndex, orderIndex = 0, 0
    tasksReturn = []
    while taskIndex < len(tasks):
        orders = tasks[taskIndex]['orders']
        taskId = tasks[taskIndex]['taskId']

        orderIndex = 0

        tasks_in_order = []
        while orderIndex < len(orders):

            orderId = orders[orderIndex]['orderId']
            receiveBin = orders[orderIndex]['receivingBinTag']

            for rack in RACKS:
                source_bins = []

                cartTotal = 0
                for source_bin in orders[orderIndex]['sourceBins']:
                    if source_bin['binTag'][0] == rack:
                        numItems = source_bin['numItems']
                        source_bins.append(SourceBin(
                            tag=source_bin['binTag'],
                            count=numItems
                        ))
                        cartTotal += numItems

                tasks_in_order.append(PickingTask(
                    task_id=taskId,
                    order_id=orderId,
                    rack=rack,
                    source_bins=source_bins,
                    receive_bin=ReceiveBin(
                        tag=receiveBin,
                        expected_count=cartTotal,
                    )
                ))

            orderIndex += 1

        tasks_ordered_by_rack = sorted(tasks_in_order, key=lambda rack_orders: rack_orders.rack)

        tasksReturn.extend(tasks_ordered_by_rack)

        taskIndex += 1
    return tasksReturn

#
# def get_paper_pick_list_tasks(data):
#     """Function which parses dictionary with experiment data from json file.
#
#     Args:
#         data (dict): dictionary of structured experiment data
#     """
#     tasks = data['tasks']
#     tasksReturn = []
#     for i, task in enumerate(tasks):
#         orders = task['orders']
#         taskId = task['taskId']
#
#         tasks_in_order = []
#         for order in orders:
#
#             orderId = order['orderId']
#             receiveBin = order['receivingBinTag']
#
#             for rack in RACKS:
#                 source_bins = []
#
#                 cartTotal = 0
#                 for source_bin in order['sourceBins']:
#                     if source_bin['binTag'][0] == rack:
#                         numItems = source_bin['numItems']
#                         source_bins.append(SourceBin(
#                             tag=source_bin['binTag'],
#                             count=numItems
#                         ))
#                         cartTotal += numItems
#
#                 tasks_in_order.append(PaperPickListRackOrder(
#                     rack_name=rack,
#                     order_id=orderId,
#                     source_bins=source_bins,
#                     recieve_bin=ReceiveBin(receiveBin, cartTotal)
#                 ))
#
#         PaperPickListRack(rack_name=rack, )
#
#
#         tasks_ordered_by_rack = sorted(tasks_in_order, key=lambda rack_orders: rack_orders.rack)
#
#         tasksReturn.extend(tasks_ordered_by_rack)
#
#     return tasksReturn
