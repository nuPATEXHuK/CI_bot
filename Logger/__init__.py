# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging
import sys

LOG_FILE_MAX_SIZE = 1024 * 1024 * 1024
LOG_FILE_MAX_BACKUP_COUNT = 5
logger = logging.getLogger('common')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)+8s]'
                              '[%(asctime)s]'
                              '[%(module)s]'
                              '[%(funcName)s:%(lineno)d] %(message)s',
                              '%d.%m.%Y %H:%M:%S')

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
