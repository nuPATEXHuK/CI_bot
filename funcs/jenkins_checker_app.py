# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep

import jenkinsapi
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

from Logger import logger
from config_loader import get_jenkins_cfg as cfg
from notification_bot import send_build_info

BASE_URL = cfg()["url"]
CRUMB = CrumbRequester(baseurl=BASE_URL)
JENKINS = Jenkins(BASE_URL, requester=CRUMB)
CHECK_BUILD_LIST = dict()
TRACKING_JOBS = cfg()['jobs']
TIMEOUT = 10


def jenkins_checker_thread():
    """Функция для периодической проверки прохождения отслеживаемых билдов"""
    while True:
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
                             'Отслеживаемая джоба: %s\n'
                             'Текст ошибки: %s', job, error)
                continue
            # Если не было до этого билдов - обновляем последний билд
            if TRACKING_JOBS[job] == 0:
                TRACKING_JOBS[job] = last_num
                logger.info('Обновлён последний билд для джобы %s', job)
            # Проверяем последний билд, если он больше текущего - значит новый
            if TRACKING_JOBS[job] < last_num:
                logger.info('Обнаружен новый билд %s джобы %s, '
                            'добавлен в отслеживаемые',
                            last_num, job)
                # Задаём особый формат для отслеживания
                tracking_job = str(job) + '.' + str(last_num)
                # Ставим признак, что он ещё не обработан
                CHECK_BUILD_LIST[tracking_job] = 'NOT_READY'
                TRACKING_JOBS[job] = last_num
                # Готовим данные для отправки в телеграмм
                job_in_url = job.replace('/', '/job/')
                job_in_telegram = job.replace('_', '\_').replace('/', '\/')
                job_for_tracking = job + '.' + str(last_num)
                # Отправляем информацию о новом билде в телеграмм
                send_build_info('*Запущен новый билд '
                                f'{last_num}\!*\n\n'
                                f'Ссылка на джобу\: {BASE_URL}/job/'
                                f'{job_in_url}/{last_num}\n'
                                f'Джоба\: {job_in_telegram}',
                                job_for_tracking)
        if len(CHECK_BUILD_LIST) == 0:
            logger.info('Нет билдов для отслеживания')
        else:
            builds_str = ''
            # Подготавливаем название билда для дальнейшей обработки из списка
            for job in CHECK_BUILD_LIST:
                build = str(job).split(".")[1]
                builds_str += f'{build} '
            logger.info('Есть билды для отслеживания: %s', builds_str)
            untracking_builds = dict()
            # Проходимся по отслеживаемым билдам
            for tracking_job in CHECK_BUILD_LIST:
                # Подготавливаем данные по билду
                job = str(tracking_job).split(".")[0]
                build = str(tracking_job).split(".")[1]
                logger.info('Проверяем билд %s джобы %s', build, job)
                build_obj = JENKINS.get_job(job).get_build(int(build))
                status = build_obj.get_status()
                logger.info('Билд №%s. Статус: %s',
                            build,
                            status)
                # Статус может быть разным,
                # если он None - значит билд в процессе
                if status is not None:
                    # Если статус не None - значит он закончился, но даём 1 шаг
                    # на обновление статуса. Отрабатывает со 2-го раза, может
                    # измениться с SUCCESS на любое другое состояние,
                    # особенность Jenkins
                    if CHECK_BUILD_LIST[tracking_job] == 'NOT_READY':
                        CHECK_BUILD_LIST[tracking_job] = 'READY'
                    # Если билд в статусе READY, можно получить настоящий статус
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
                        # Если билд завершён - добавляем его в untracking_builds
                        untracking_builds[job] = build
                        # Пробуем получить длительность билда
                        try:
                            duration = str(build_obj.get_duration()).split(
                                '.', maxsplit=1)[0].replace(':', '\:')
                        except Exception as e:
                            duration = '\?'
                            logger.error('Ошибка при разборе отчёта\n%s', e)
                        # Подготавливаем данные для телеграмм
                        job_in_url = tracking_job.split('.')[0] \
                            .replace('/', '/job/')
                        job_in_telegram = job.replace('_', '\_').replace('/',
                                                                         '\/')
                        # Отправляем финальное сообщение о завершении билда
                        send_build_info(
                            f'*Сборка билда {build} завершена\!*\n\n'
                            f'Джоба\: {job_in_telegram}\n'
                            f'Результат\: {result_build}\n'
                            f'Длительность\: {duration}\n',
                            tracking_job,
                            True)
            # Убираем все законченные билды из отслеживаемых
            for untracking_job in untracking_builds:
                element = (f'{untracking_job}.'
                           f'{untracking_builds[untracking_job]}')
                CHECK_BUILD_LIST.pop(element)
        logger.info('Проверка завершена, запущено ожидание в %s секунд',
                    TIMEOUT)
        sleep(TIMEOUT)
