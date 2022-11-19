
import logging
from logging.handlers import TimedRotatingFileHandler

log_file_name = 'Error.log'
logger_name = 'DiscordBot'

def get_logger():
    return logging.getLogger(logger_name)

def init_logger(logger = 'DiscordBot', log_file = 'DiscordBot.log', log_level=logging.DEBUG):
    global log_file_name,logger_name
    log_file_name = log_file
    logger_name = logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    # create file handler which logs even debug messages
    fh = TimedRotatingFileHandler(log_file_name, when="midnight", interval=1)
    fh.suffix = "%Y%m%d"
    fh.setLevel(log_level)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)10s - %(filename)20s - %(funcName)30s() - %(lineno)3s | %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)