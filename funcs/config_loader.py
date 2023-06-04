# -*- coding: utf-8 -*-
# для парсинга CFG файлов
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read(Path.cwd() / 'data' / 'config.cfg')


def get_ntf_token() -> str:
    """
    Получение токена бота запуска билдов из конфига

    :return: токен бота
    """
    token = config.get('main', 'ntf_token')
    return token


def get_exc_token() -> str:
    """
    Получение токена бота уведомлений из конфига

    :return: токен бота
    """
    token = config.get('main', 'exc_token')
    return token


def get_chat_id() -> str:
    """
    Получение ID чата для оповещений из конфига

    :return: ID чата
    """
    chat_id = config.get('main', 'info_chat_id')
    return chat_id


def get_jenkins_cfg() -> dict:
    """
    Получение данных для Jenkins

    :return: [url, jobs]
    """
    url = config.get('jenkins', 'url')
    jobs = config.get('jenkins', 'jobs').split(';')
    jobs_dict = dict()
    for job in jobs:
        jobs_dict[job] = 0
    return {'url': url, 'jobs': jobs_dict}
