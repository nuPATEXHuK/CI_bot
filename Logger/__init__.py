# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging
# модуль питона
import sys
from logging.handlers import RotatingFileHandler

LOG_FILE_MAX_SIZE = 1024 * 1024 * 1024
LOG_FILE_MAX_BACKUP_COUNT = 5
# получение стандартного логгера
logger = logging.getLogger('common')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)+8s]'
                              '[%(asctime)s]'
                              '[%(module)s]'
                              '[%(funcName)s:%(lineno)d] %(message)s',
                              '%d.%m.%Y %H:%M:%S')

# стандартное добавление в логи по тому как мы настроили выше
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = RotatingFileHandler(filename='Logs/bot.log',
                                   maxBytes=1048576,
                                   backupCount=10,
                                   encoding='utf-8',
                                   mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
