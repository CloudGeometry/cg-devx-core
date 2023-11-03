import logging

logger = logging.getLogger('cgdevx.custom_logger')
# Set the default logging level to CRITICAL. 
# This means that only CRITICAL messages will be logged by default.
logger.setLevel(logging.CRITICAL)

# Create a StreamHandler that will output log messages to the console.
handler = logging.StreamHandler()
# Create a formatter that will format the log messages.
# The format includes the time, logger name, logging level, and the actual message.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Set the formatter for the handler.
handler.setFormatter(formatter)
# Add the handler to the logger.
logger.addHandler(handler)


def configure_logging(verbosity: str) -> None:
    """
    Configures the logging level based on the given verbosity.

    Args:
        verbosity (str): The verbosity level. Should be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'.
    """
    # Set the global logging level based on the verbosity argument.
    logging.basicConfig(level=getattr(logging, verbosity, logging.CRITICAL))
    # Set the custom logger's level based on the verbosity argument.
    logger.setLevel(getattr(logging, verbosity, logging.CRITICAL))
