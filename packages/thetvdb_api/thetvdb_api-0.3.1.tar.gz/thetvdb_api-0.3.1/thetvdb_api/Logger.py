# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler

class Logger(object):
  def __init__(self, name, log_level, log_path=False):
    self.logger = self.set_logger(name)
    self.set_console_logger(self.logger, log_level)
    
    if log_path:
      self.set_file_logger(self.logger, log_path, log_level)
  
  def set_logger(self, name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    return logger
    
  def set_console_logger(self, logger, level=logging.INFO, format='[%(levelname)s] %(message)s'):
    formatter = logging.Formatter(format)
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(level)
    steam_handler.setFormatter(formatter)
    logger.addHandler(steam_handler)
        
  def set_file_logger(self, logger, path, level=logging.INFO, format='%(asctime)s :: [%(levelname)s] %(message)s'):
    formatter = logging.Formatter(format)
    file_handler = RotatingFileHandler(path, 'a', 1000000, 1)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
  def get_logger(self):
    return self.logger