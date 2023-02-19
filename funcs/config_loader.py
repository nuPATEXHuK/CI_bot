# -*- coding: utf-8 -*-
import configparser
from pathlib import Path
from typing import List

config = configparser.ConfigParser()
config.read(Path.cwd() / 'data' / 'config.cfg')


def get_token() -> str:
    """
    Получение токена бота из конфига

    :return: токен бота
    """
    token = config.get('main', 'token')
    return token


def get_chat_id() -> str:
    """
    Получение ID чата для оповещений из конфига

    :return: ID чата
    """
    chat_id = config.get('main', 'info_chat_id')
    return chat_id
