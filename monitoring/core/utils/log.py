import os
import logging
from colorlog import ColoredFormatter

def setup_custom_logger(name, file: str, log_level = logging.DEBUG):

    logger = logging.getLogger(name)

    # Setup colored logging for console
    consoleFormatter  = ColoredFormatter(
        '%(green)s%(asctime)s%(reset)s - %(cyan)s%(module)s %(process)d%(reset)s - %(log_color)s%(levelname)s%(reset)s - %(message)s'
    )

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(consoleFormatter)
    logger.addHandler(consoleHandler)

    # Setup file logging
    if(file):
        fileFormatter = logging.Formatter('%(asctime)s - %(module)s %(process)d - %(levelname)s - %(message)s')
        fileHandler = logging.FileHandler(file)
        fileHandler.setFormatter(fileFormatter)
        logger.addHandler(fileHandler)
    
    logger.setLevel(log_level)

    return logger

logger = setup_custom_logger('logger', './log')
