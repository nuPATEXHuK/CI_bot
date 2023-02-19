# -*- coding: utf-8 -*-
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks
# pylint: disable=use-list-literal
# pylint: disable=use-dict-literal
from typing import Optional, List, Dict

import funcs.check_funcs as check
from funcs import config_loader as cfg
from Logger import logger

CHAT_ID = int(cfg.get_chat_id())


def add_build() -> str:
    """
    Запуск нового билда

    :return: результат запуска билда или причина, почему билд не запущен
    """
    logger.info('Запущено добавление нового билда')
    if check.release_chat_exist(chat_id):
        return 'Релиз этого чата уже существует'
    if check.release_code_exist(code):
        return 'Релиз с таким кодом уже существует'
    errors = dbf.add_release(chat_id, code)
    if not errors:
        logger.info('Релиз добавлен')
        return 'Релиз добавлен'
    return errors


def edit_release_in_db(chat_id: int, params_dict: dict) -> str:
    """
    Изменение параметров релиза, привязанного к чату

    :param chat_id: ID чата, где вызвана команда
    :param params_dict: параметры для изменения релиза
    :return: информация об изменённых параметрах релиза
    """
    if not check.release_chat_exist(chat_id):
        return 'Релиз, привязанный к этому чату, не найден'
    release_code = dbf.get_release_code_by_chat(chat_id)
    new_params = get_new_release_params_dict(params_dict, release_code)
    if not new_params:
        return 'Новые параметры релиза не заданы'
    response = dbf.set_new_param_value(new_params, release_code)
    return response


def edit_work_group_in_db(chat_id: int, params_dict: dict) -> str:
    """
    Изменение списка пользователей по ролям, привязанных к релизу

    :param chat_id: ID чата, где вызвана команда
    :param params_dict: параметры для изменения ролей на релизе
    :return: информация об изменённом списке пользователей
    """
    if not check.release_chat_exist(chat_id):
        return 'Релиз, привязанный к этому чату, не найден'
    release_code = dbf.get_release_code_by_chat(chat_id)
    new_params = get_new_users_params_dict(params_dict, release_code)
    if not new_params:
        return 'Новые пользователи в группах не заданы'
    dbf.set_new_param_value(new_params, release_code)
    return 'Рабочая группа релиза изменена'


def start_release(chat_id: int, reset: bool) -> str:
    """
    Запуск релиза в работу

    :param chat_id: ID чата, где вызвана команда
    :param reset: параметр сброса текущего времени по этапам релиза
    :return: статус релиза
    """
    if not check.release_chat_exist(chat_id):
        return 'Релиз, привязанный к этому чату, не найден'
    release_code = dbf.get_release_code_by_chat(chat_id)
    if check.release_already_start(release_code):
        return 'Релиз уже запущен в работу'
    dbf.start_release(release_code, reset)
    return 'Релиз запущен'


def stop_release(chat_id: int) -> str:
    """
    Остановка активности релиза с сохранением текущих параметров

    :param chat_id: ID чата, где вызвана команда
    :return: статус релиза
    """
    if not check.release_chat_exist(chat_id):
        return 'Релиз, привязанный к этому чату, не найден'
    release_code = dbf.get_release_code_by_chat(chat_id)
    if not check.release_already_start(release_code):
        return 'Релиз уже остановлен'
    dbf.stop_release(release_code)
    return 'Релиз остановлен'


def get_release_status(chat_id: int) -> str:
    """
    Получение статуса релиза (активен или остановлен)

    :param chat_id: ID чата, где вызвана команда
    :return: статус релиза
    """
    if not check.release_chat_exist(chat_id):
        return 'Релиз, привязанный к этому чату, не найден'
    release_code = dbf.get_release_code_by_chat(chat_id)
    status = dbf.get_status_by_code(release_code)
    if int(status[0]) != 0:
        return f'Релиз в работе, текущий этап: {status[1]}'
    return 'Релиз остановлен или не запущен'


def get_releases_list() -> str:
    """
    Получение списка активных релизов

    :return: список активных релизов или сообщение об их отсутствии
    """
    answer = 'Список активных релизов:\n'
    releases = dbf.get_active_releases_list()
    if len(releases) < 1:
        answer = 'Нет активных релизов'
    else:
        for release in releases:
            answer += (f'•\t{release[0]}. Серия: {release[2]}. '
                       f'Текущий этап: {release[1]}\n')
    return answer


def check_releases(wait_time: int) -> Optional[List[List]]:
    """
    Проверка всех активных релизов на срок сдачи (4 раза за этап работы)

    :param wait_time: таймаут шедулера в минутах
    :return: список релизов с сообщениями в них или None
    """
    active_releases_code = dbf.get_active_releases_code()
    if len(active_releases_code) < 1:
        return None
    answer = list()
    for code in active_releases_code:
        release_data = dbf.get_release_data_by_code(code)
        chat_id = int(release_data['chat_id'])
        stage = str(release_data['stage'])
        admin = str(release_data['admin'])
        std_time = int(release_data[f'{stage}_std_time'])
        stage_key = f'{stage}_current_time'
        cur_time = int(release_data[stage_key])
        cur_time -= wait_time
        cur_release_time = int(release_data['release_time'])
        dbf.set_new_param_value({stage_key: cur_time,
                                 'release_time': cur_release_time - wait_time},
                                code)
        step = std_time / 4
        if cur_time % step == 0 and cur_time <= std_time:
            skip = check.check_skip_alert()
            users = str(release_data[f'{stage}_users']).split('/')
            alert = ''
            if cur_time > 0:
                alert += f'\nДо конца срока этапа {stage} ' \
                         f'осталось: {round(cur_time / 60, 2)} ч.'
            else:
                skip = False
                if len(users) > 0 and users[0] != 'None':
                    for user in users:
                        alert += f'@{user} '
                    alert += f'@{admin}'
                else:
                    alert += f'@{admin}'
                if cur_time == 0:
                    alert += f'\nЭтап {stage} просрочен!'
                else:
                    alert += f'\nЭтап {stage} просрочен! Просрочка ' \
                             f'составляет: {-round(cur_time / 60, 2)} ч.'
            if not skip:
                answer.append([chat_id, alert])
    if len(answer) < 1:
        return None
    return answer


def get_new_release_params_dict(params: dict,
                                release_code: str) -> Optional[Dict]:
    """
    Проверка и возврат новых параметров релиза (без незаполненных и одинаковых)

    :param params: список новых параметров релиза
    :param release_code: код релиза
    :return: список новых параметров или None
    """
    new_params = dict()
    for key in params.keys():
        new_param_value = params[key]
        if new_param_value == 'NULL':
            new_params[key] = new_param_value
            continue
        if new_param_value:
            param_from_db = dbf.get_param(key, release_code)
            if param_from_db == new_param_value:
                continue
            if key not in {'name', 'code'}:
                if 'std_time' in key:
                    new_params[key] = int(new_param_value) * 60
                else:
                    new_params[key] = int(new_param_value)
            else:
                if key == 'code':
                    if check.release_code_exist(new_param_value):
                        continue
                new_params[key] = new_param_value
    if len(new_params) < 1:
        return None
    return new_params


def get_new_users_params_dict(params: dict,
                              release_code: str) -> Optional[Dict]:
    """
    Проверка и возврат новых пользователей на ролях релиза
    (без незаполненных и одинаковых)

    :param params: список новых пользователей по группам
    :param release_code: код релиза
    :return: список новых пользователей по группам или None
    """
    new_params = dict()
    for key in params.keys():
        if not params[key]:
            continue
        new_param_value = str(params[key]).replace('@', '')
        param_from_db = str(dbf.get_param(key,
                                          release_code)).replace('/', ',')
        if param_from_db == new_param_value:
            continue
        user_list = str(new_param_value).split(',')
        new_users = ''
        for user in user_list:
            new_users += user + '/'
        if new_users:
            new_users = new_users[:-1]
        new_params[key] = new_users
    if len(new_params) < 1:
        return None
    return new_params


def new_tag(chat_id: int, tag: str) -> Optional[str]:
    """
    Обнаружение нового тега для переключения между этапами и сериями

    :param chat_id: ID чата
    :param tag: полученный тег
    :return: если произошло переключение этапов или серии - информация об этом
    """
    if not check.release_chat_exist(chat_id):
        return None
    code = dbf.get_release_code_by_chat(chat_id)
    started = check.release_already_start(code)
    if not started:
        return None
    stage = dbf.get_param('stage', code)
    if stage == tag:
        if stage == 'final':
            last_ep = dbf.new_ep(code)
            if last_ep:
                return 'Работа над релизом закончена'
            return 'Работа над серией закончена'
        dbf.new_stage(stage, code)
        return f'Этап {stage} закончен'
    return None


def get_help() -> str:
    """
    Получение справки по боту

    :return: справка по боту
    """
    answer = 'Справка по боту\n\n'
    answer += ('Список команд:\n'
               '•/release_add [code] - добавление релиза с уникальным кодом\n'
               '•/edit_release [param_name=value, ...] - настройка релиза\n'
               'Параметры:\n'
               'name - имя релиза без пробелов (можно использовать "_")\n'
               'code - уникальный код релиза\n'
               'fast - 0 или 1, корректирует время этапов релиза\n'
               'top - 0 или 1, корректирует время этапов релиза\n'
               'current_ep - текущий эпизод релиза (по умолчанию 0)\n'
               'max_ep - максимальный эпизод релиза\n'
               '(параметры с std_time указывать при особых случаях, если '
               'нужно стандартное время в зависимости от типа релиза - '
               'использовать значение NULL для очистки)\n'
               'role_std_time - время на расписывание ролей в часах\n'
               'voice_std_time - время на озвучку в часах\n'
               'timer_std_time - время на тайминг сведение в часах\n'
               'fix_std_time - время на фиксы от войсеров в часах\n'
               'final_std_time - время на финальную обработку серии в часах\n'
               '•/edit_work_group [param_name=value, ...] - настройка рабочей '
               'группы релиза\n'
               'Параметры:\n'
               'role_users - ник пользователя, который расписывает роли\n'
               'voice_users - список ников войсеров через запятую\n'
               'timer_users - ник таймера\n'
               'fix_users - ник таймера для проверки сданных фиксов\n'
               'final_users - ник таймера для завершения сборки серии\n'
               'admin_users - ник администратора релиза\n'
               '•/release_start [reset] - старт релиза (если нужен сброс '
               'текущего времени - использовать параметр reset через пробел)\n'
               '•/release_stop - остановка работы релиза\n'
               '•/release_status - отображение статуса релиза\n'
               '•/release_list - список активных релизов\n\n'
               'Управление ботом:\nХештеги отправлять только после завершения '
               'всех действий по текущему этапу\n'
               '•#role - завершить этап расписывания ролей\n'
               '•#voice - завершить этап озвучки\n'
               '•#timer - завершить этап тайминга и сведения\n'
               '•#fix - завершить этап записи фиксов\n'
               '•#final - завершить этап финальной обработки серии, '
               'начать новый эпизод\n'
               'Если указан max_ep и текущая серия последняя, то после '
               'отправки #final релиз перейдёт в неактивное состояние')
    return answer


def test_func() -> str:
    """
    Тестовая функция для отладки

    :return: тестовые данные
    """
    status = check.release_already_start('test_release')
    if status:
        answer = 'Релиз запущен'
    else:
        answer = 'Релиз остановлен'
    return answer
