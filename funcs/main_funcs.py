# -*- coding: utf-8 -*-

import bot
from funcs import config_loader as cfg
from funcs import jenkins_app as jks
from Logger import logger

CHAT_ID = int(cfg.get_chat_id())


def add_build() -> str:
    """
    Запуск нового билда

    :return: результат запуска билда или причина, почему билд не запущен
    """
    logger.info('Запущено добавление нового билда')
    errors = jks.new_build()
    if not errors:
        logger.info('Билд запущен')
        return 'Билд запущен'
    return errors


def send_message(message: str, build_info: str):
    """
    Отправка сообщения в чат

    :param message: сообщение для отправки
    :param build_info: информация о билде для отслеживания
    """
    bot.send_build_info(message=message, build_info=build_info)


def send_end_build_message(message: str, build_info: str):
    """
    Отправка сообщения в чат

    :param message: сообщение для отправки
    :param build_info: информация о билде для отслеживания
    """
    bot.send_build_info(message=message, build_info=build_info, finish=True)


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
