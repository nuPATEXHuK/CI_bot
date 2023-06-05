# -*- coding: utf-8 -*-

from Logger import logger
from funcs import config_loader as cfg
from funcs import jenkins_builder_app as jks

CHAT_ID = int(cfg.get_chat_id())


def add_build() -> str:
    """
    Запуск нового билда

    :return: результат запуска билда или причина, почему билд не запущен
    """
    logger.info('Запущено добавление нового билда')
    errors = jks.new_build()
    # Если не вернулись ошибки:
    if errors and len(errors) > 0:
        return str(errors)
    else:
        logger.info('Билд запущен')
        return 'Билд запущен'


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
