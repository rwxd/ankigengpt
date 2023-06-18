import logging
import logging.handlers
from sys import stderr

logger = logging.getLogger('ankigengpt')

logger.setLevel('DEBUG')


def init_logger(debug: bool) -> None:
    logging_format = (
        '%(levelname)s - %(asctime)s - %(name)s - '
        + '%(filename)s - %(funcName)s - %(lineno)s - %(message)s'
    )
    default_formatter = logging.Formatter(logging_format)
    default_stream_handler = logging.StreamHandler(stderr)
    if debug:
        default_stream_handler.setLevel('DEBUG')
    else:
        default_stream_handler.setLevel('WARNING')
    default_stream_handler.setFormatter(default_formatter)
    logger.addHandler(default_stream_handler)
