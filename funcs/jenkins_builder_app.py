# -*- coding: utf-8 -*-
from typing import Optional

import jenkinsapi
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

from Logger import logger
from config_loader import get_jenkins_cfg as cfg

BASE_URL = cfg()["url"]
CRUMB = CrumbRequester(baseurl=BASE_URL)
JENKINS = Jenkins(BASE_URL, requester=CRUMB)
CHECK_BUILD_LIST = dict()
TRACKING_JOBS = cfg()['jobs']


def new_build() -> Optional[list]:
    """
    Функция для запуска нового билда
    :return: Текст ошибки при неудачном билде
    """
    global JENKINS
    # Проходимся по всем указанным джобам для запуска
    # Без расширения функции build_add в notification_bot.py
    # будут запускаться все джобы
    error_list = list()
    for job in TRACKING_JOBS:
        # Проверяем последний билд, может выдать исключение, обрабатываем
        try:
            last_build = JENKINS.get_job(job).get_last_build()
            last_num = last_build.get_number()
        # Предыдущих билдов не было, устанавливаем первый билд
        except jenkinsapi.custom_exceptions.NoBuildData:
            last_num = 0
        # Ошибка соединения, скипаем запуск билда
        except ConnectionError as error:
            error_text = ('Ошибка получения последнего билда с дженкинса.\n'
                          f'Отслеживаемая джоба: {job}'
                          f'Текст ошибки: {error}')
            logger.error(error_text)
            error_list.append(error_text)
            continue
        # Попытка запустить джобу с обработкой исключений
        try:
            JENKINS.build_job(job)
            TRACKING_JOBS[job] = last_num + 1
            logger.info('Запущен новый билд для джобы %s', job)
        # Если словили любую ошибку, записываем её и скипаем текущую джобу
        except Exception as error:
            error_text = ('Ошибка запуска нового билда:\n'
                          f'Отслеживаемая джоба: {job}'
                          f'Текст ошибки: {error}')
            logger.error(error_text)
            error_list.append(error_text)
            continue
    if len(error_list) > 0:
        return error_list
