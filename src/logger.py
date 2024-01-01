import os
import logging
import shutil

def logger_setup() -> None:
    """Set up the logger"""

    logs_dir = "logs"
    if os.path.exists(logs_dir):
        shutil.rmtree(logs_dir)
    os.makedirs(logs_dir)

    # Define log format
    log_format = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    date_format = '%H:%M:%S'

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Define log files
    debug_log_name = 'debug.log'
    info_log_name = 'info.log'

    debug_log_path = os.path.join(logs_dir, debug_log_name)
    info_log_path = os.path.join(logs_dir, info_log_name)

    debug_log_fh = logging.FileHandler(debug_log_path, 'w', 'utf8')
    info_log_fh = logging.FileHandler(info_log_path, 'w', 'utf8')

    debug_log_fh.setLevel(logging.DEBUG)
    info_log_fh.setLevel(logging.INFO)

    debug_log_fh.setFormatter(formatter)
    info_log_fh.setFormatter(formatter)

    # Define log that be sent to streams
    # console_h = logging.StreamHandler()
    # console_h.setLevel(logging.DEBUG)
    # console_h.setFormatter(formatter)

    # Define the logger
    logger_root = logging.getLogger()
    logger_root.setLevel(logging.DEBUG)
    logger_root.addHandler(debug_log_fh)
    logger_root.addHandler(info_log_fh)
    # logger_root.addHandler(console_h)

    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)