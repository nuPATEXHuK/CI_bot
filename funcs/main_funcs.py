# -*- coding: utf-8 -*-

import threading
from bot import send_build_info
from Logger import logger
from funcs import config_loader as cfg
from funcs import jenkins_app as jks

CHAT_ID = int(cfg.get_chat_id())


def add_build() -> str:
    """
    Запуск нового билда

    :return: результат запуска билда или причина, почему билд не запущен
    """
    logger.info('Запущено добавление нового билда')
    errors = jks.new_build()
    # Если не вернулись ошибки:
    if len(errors) < 1:
        logger.info('Билд запущен')
        return 'Билд запущен'
    return str(errors)


def send_message(message: str, build_info: str):
    """
    Отправка сообщения в чат

    :param message: сообщение для отправки
    :param build_info: информация о билде для отслеживания
    """
    send_build_info(message=message, build_info=build_info)


def send_end_build_message(message: str, build_info: str):
    """
    Отправка сообщения в чат

    :param message: сообщение для отправки
    :param build_info: информация о билде для отслеживания
    """
    send_build_info(message=message, build_info=build_info, finish=True)


def get_help() -> str:
    """
    Получение справки по боту

    :return: справка по боту
    """
    answer = 'Справка по боту\n\n'
    answer += ('Список команд:\n'
               '* build - запуск нового билда')
    return answer


def test_func() -> str:
    """
    Тестовая функция для отладки

    :return: тестовые данные
    """
    answer = "Тестовая функция"
    return answer


def jenkins_thread():
    # Создание и запуск отдельного треда чекера дженкинса
    logger.info('Запуск треда дженкинса на проверку билдов')
    jenkins_main_thread = threading.Thread(name='jenkins_checker_thread',
                                           target=jks.jenkins_checker_thread,
                                           daemon=True)
    jenkins_main_thread.start()


jenkins_thread()
