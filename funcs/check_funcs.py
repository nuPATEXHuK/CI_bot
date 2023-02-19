# -*- coding: utf-8 -*-
from datetime import datetime

import funcs.database_funcs as dbf


def release_chat_exist(chat_id: int) -> bool:
    """
    Проверка существования релиза, привязанного к чату

    :param chat_id: ID чата
    :return: существует релиз или нет
    """
    code = dbf.get_release_code_by_chat(chat_id)
    if code == 'None':
        return False
    return True


def release_code_exist(code: str) -> bool:
    """
    Проверка на существования релиза с указанным кодом

    :param code: уникальный код релиза
    :return: существует такой релиз или нет
    """
    code_list = dbf.get_code_from_all_releases()
    for code_from_db in code_list:
        if dbf.formate_one(str(code_from_db)) == code:
            return True
    return False


def release_already_start(code: str) -> bool:
    """
    Проверка, находится ли релиз в работе

    :param code: уникальный код релиза
    :return: релиз в работе или нет
    """
    return bool(int(dbf.get_param('status', code)))


def check_skip_alert() -> bool:
    """
    Проверка времени заглушки уведомлений

    :return: флаг, заглушаем ли мы уведомления
    """
    skip = False
    now = datetime.now().strftime('%H:%M')
    target = dbf.SLEEP_TIMES
    now_hour = int(now.split(':')[0])
    now_min = int(now.split(':')[1])
    target_start_hour = int(target[0].split(':')[0])
    target_start_min = int(target[0].split(':')[1])
    target_final_hour = int(target[1].split(':')[0])
    target_final_min = int(target[1].split(':')[1])

    if target_start_hour < now_hour < target_final_hour:
        skip = True
    else:
        if target_start_min < now_min < target_final_min:
            skip = True
    return skip
