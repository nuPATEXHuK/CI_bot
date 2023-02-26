# -*- coding: utf-8 -*-
from datetime import datetime
from config_loader import get_jenkins_cfg as cfg

import jenkinsapi
import requests
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

from main_funcs import send_message, send_end_build_message
from Logger import logger

BASE_URL = cfg()["url"]
CRUMB = CrumbRequester(baseurl=BASE_URL)
JENKINS = Jenkins(BASE_URL, requester=CRUMB)
CHECK_BUILD_LIST = dict()
TRACKING_JOBS = cfg()['jobs']


def new_build():
    """
    Функция для запуска нового билда
    :return: Текст ошибки при неудачном билде
    """
    global JENKINS
    for job in TRACKING_JOBS:
        try:
            last_build = JENKINS.get_job(job).get_last_build()
            last_num = last_build.get_number()
        except jenkinsapi.custom_exceptions.NoBuildData:
            last_num = 0
        except ConnectionError as error:
            error_text = ('Ошибка получения последнего билда с дженкинса.\n'
                          f'Отслеживаемая джоба: {job}'
                          f'Текст ошибки: {error}')
            logger.error(error_text)
            return error_text
        if TRACKING_JOBS[job] == 0:
            TRACKING_JOBS[job] = last_num + 1
            logger.info('Запущен новый билд для джобы %s', job)
            JENKINS.build_job(job)


def jenkins_checker():
    """Функция для периодической проверки прохождения отслеживаемых билдов"""
    logger.info('Jenkins checker run at %s', datetime.now())
    global JENKINS
    # Проходимся по джобам, добавляем новые билды в отслеживаемые
    for job in TRACKING_JOBS:
        try:
            last_build = JENKINS.get_job(job).get_last_build()
            last_num = last_build.get_number()
        except jenkinsapi.custom_exceptions.NoBuildData:
            last_build = None
            last_num = 0
        except ConnectionError as error:
            logger.error('Ошибка получения последнего билда с дженкинса.\n'
                         f'Отслеживаемая джоба: {job}'
                         f'Текст ошибки: {error}')
            continue
        if TRACKING_JOBS[job] == 0:
            TRACKING_JOBS[job] = last_num
            logger.info('Обновлён последний билд для джобы %s', job)
        if TRACKING_JOBS[job] < last_num:
            logger.info('Обнаружен новый билд %s джобы %s, '
                        'добавлен в отслеживаемые',
                        last_num, job)
            tracking_job = str(job) + '.' + str(last_num)
            CHECK_BUILD_LIST[tracking_job] = 'NOT_READY'
            TRACKING_JOBS[job] = last_num
            job_in_url = job.replace('/', '/job/')
            job_in_telegram = job.replace('_', '\_').replace('/', '\/')
            job_for_tracking = job + '.' + str(last_num)
            send_message(f'*Запущен новый билд [{last_num}]({BASE_URL}/job/'
                            f'{job_in_url}/{last_num})\!*\n\n'
                            f'Джоба\: {job_in_telegram}\n',
                            job_for_tracking)
    if len(CHECK_BUILD_LIST) == 0:
        logger.info('Нет билдов для отслеживания')
    else:
        builds_str = ''
        for job in CHECK_BUILD_LIST.keys():
            build = str(job).split(".")[1]
            builds_str += f'{build} '
        logger.info('Есть билды для отслеживания: %s', builds_str)
        untracking_builds = dict()
        for tracking_job in CHECK_BUILD_LIST.keys():
            job = str(tracking_job).split(".")[0]
            build = str(tracking_job).split(".")[1]
            logger.info('Проверяем билд %s джобы %s', build, job)
            build_obj = JENKINS.get_job(job).get_build(int(build))
            status = build_obj.get_status()
            logger.info('Билд №%s. Статус: %s',
                        build,
                        status)
            if status is not None:
                if CHECK_BUILD_LIST[tracking_job] == 'NOT_READY':
                    CHECK_BUILD_LIST[tracking_job] = 'READY'
                elif CHECK_BUILD_LIST[tracking_job] == 'READY':
                    result_build = '🟦 Неизвестно'
                    if status == 'SUCCESS':
                        result_build = '🟩 Успешно'
                    elif status == 'ABORTED':
                        result_build = '🟪 Отменён'
                    elif status == 'FAILURE':
                        result_build = '🟥 Провалена сборка билда'
                    elif status == 'UNSTABLE':
                        result_build = '🟨 Есть ошибки в тестах'
                    untracking_builds[job] = build
                    try:
                        duration = str(build_obj.get_duration()).split(
                            '.', maxsplit=1)[0].replace(':', '\:')
                    except Exception as e:
                        duration = '\?'
                        logger.error('Ошибка при разборе отчёта\n%s', e)
                    job_in_url = tracking_job.split('.')[0] \
                        .replace('/', '/job/')
                    job_in_telegram = job.replace('_', '\_').replace('/', '\/')
                    send_end_build_message(
                        f'*Сборка билда {build} завершена\!*\n\n'
                        f'Джоба\: {job_in_telegram}\n'
                        f'Результат\: {result_build}\n'
                        f'Длительность\: {duration}\n'
                        f'[Ссылка на отчёт]({BASE_URL}/job/'
                        f'{job_in_url}/{build}/allure/)',
                        tracking_job)
        for untracking_job in untracking_builds.keys():
            element = f'{untracking_job}.{untracking_builds[untracking_job]}'
            CHECK_BUILD_LIST.pop(element)
