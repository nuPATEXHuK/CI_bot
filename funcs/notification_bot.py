# -*- coding: utf-8 -*-
# pylint: disable=import-error
import logging

import telegram
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Кастомные логи для телеграмм
from Logger import logger
# конфиги необходимые
from funcs import config_loader as cfg

# загрузка базового логгинга (можно менять уровень
# логов info, debag, errors, warnings)
logging.basicConfig(level=logging.INFO)

# Для работы бота в телеграмм
TOKEN = cfg.get_ntf_token()
BOT = telegram.Bot(token=TOKEN)
# то куда мы будем выводить, информация о билде
CHAT_ID = cfg.get_chat_id()
TRACKING_BUILDS = {}


# Стартовая функция
def start(update: Update, context: CallbackContext):
    """
    Запускается при первом запуске бота или при команде /start

    :param message: входящая команда /start
    """
    if len(TRACKING_BUILDS) > 0:
        build_list = list()
        for current_build in TRACKING_BUILDS.keys():
            build_list.append(str(current_build))
        builds = ', '.join(build_list)
    else:
        builds = 'нет'
    update.message.reply_text(f'Бот работает! '
                              f'Отслеживаемые билды: {builds}')


def send_build_info(message: str, build_info: str, finish: bool = False):
    """Отправка статуса билда в канал

    :param finish: флаг завершения отслеживания
    :param build_info: Номер билда и джоба для привязки сообщений
    :param message: Текст, отправляемый в телеграм-канал"""
    if not finish:
        msg = BOT.send_message(chat_id=CHAT_ID,
                               text=message,
                               parse_mode='MarkdownV2')
        TRACKING_BUILDS[build_info] = msg.message_id
    else:
        BOT.send_message(chat_id=CHAT_ID,
                               text=message,
                               parse_mode='MarkdownV2',
                               reply_to_message_id=TRACKING_BUILDS[build_info])
        TRACKING_BUILDS.pop(build_info)


# Стартовая функция для запуска бота.
def tlg_ntf_thread():
    logger.info('Начало прослушки и готовности ботом принимать '
                'команды (long polling)')
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, start))
    updater.start_polling(poll_interval=1.0)
