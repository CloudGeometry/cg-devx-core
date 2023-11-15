import logging


# Create a formatter that will format the log messages.
# The format includes the time, logger name, logging level, and the actual message.
class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger()
# Set the default logging level to CRITICAL.
# This means that only CRITICAL messages will be logged by default.
logger.setLevel(logging.CRITICAL)

# Create a StreamHandler that will output log messages to the console.
handler = logging.StreamHandler()
# Set the formatter for the handler.
handler.setFormatter(CustomFormatter())
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
