# -*- coding: utf-8 -*-
import threading
from datetime import datetime
from time import sleep

from Logger import logger
from funcs.execution_bot import tlg_exc_thread
from funcs.jenkins_checker_app import jenkins_checker_thread
from funcs.notification_bot import tlg_ntf_thread


def main():
    logger.info('Service started at %s', datetime.now())

    telegram_ntf_main_thread = threading.Thread(name='tlg_ntf_main_thread',
                                                target=tlg_ntf_thread,
                                                daemon=True)
    telegram_exc_main_thread = threading.Thread(name='tlg_exc_main_thread',
                                                target=tlg_exc_thread,
                                                daemon=True)
    jenkins_main_thread = threading.Thread(name='jnk_thread',
                                           target=jenkins_checker_thread,
                                           daemon=True)
    telegram_ntf_main_thread.start()
    telegram_exc_main_thread.start()
    jenkins_main_thread.start()

    while True:
        sleep(5)


if __name__ == '__main__':
    main()
