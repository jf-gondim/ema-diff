import sys
import logging

def configure_logger(name):
    """
    Configure and return a logger with the provided name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger object.
    """
    # Define the log level for the console
    console_log_level = logging.DEBUG

    # Create a logger with the provided name
    logger = logging.getLogger(name)

    # Create a handler for the console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)

    # Define the format of the log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    # Set the log level for the logger and the handler
    logger.setLevel(logging.DEBUG)
    console_handler.setLevel(console_log_level)

    return logger

# Constant for the debug level (not used in the current code, but kept as a reference)
DEBUG = logging.DEBUG
