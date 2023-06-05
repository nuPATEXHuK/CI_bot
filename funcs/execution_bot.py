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
# функции необходимы для работы
from funcs import main_funcs as mf

# загрузка базового логгинга (можно менять уровень
# логов info, debag, errors, warnings)
logging.basicConfig(level=logging.INFO)

# Для работы бота в телеграмм
TOKEN = cfg.get_ntf_token()
BOT = telegram.Bot(token=TOKEN)
# то куда мы будем выводить, информация о билде
CHAT_ID = cfg.get_chat_id()


# Стартовая функция
def start(update: Update, context: CallbackContext) -> None:
    """
    Запускается при первом запуске бота или при команде /start

    :param message: входящая команда /start
    """
    update.message.reply_text('Бот запуска билдов')


def test(update: Update, context: CallbackContext) -> None:
    """
    Тестовая функция для отладки

    :param message: входящая команда /test
    """
    answer = mf.test_func()
    if answer:
        update.message.reply_text(answer)
    else:
        update.message.reply_text('Ничего не вернулось')


def build_add(update: Update, context: CallbackContext) -> None:
    """
    Запуск нового билда на сборку (возможно расширение
    функции для указания конкретного билда)

    :param message: входящая команда /build
    """
    answer = mf.add_build()
    update.message.reply_text(answer)


def get_help(update: Update, context: CallbackContext) -> None:
    """
    Получение справки по боту

    :param message: входящая команда /help
    """
    answer = mf.get_help()
    if answer:
        update.message.reply_text(answer)
    else:
        update.message.reply_text('Ничего не вернулось')


# Стартовая функция для запуска бота.
def tlg_exc_thread():
    logger.info('Начало прослушки и готовности ботом принимать '
                'команды (long polling)')
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(Filters.command, start))
    dispatcher.add_handler(
        MessageHandler(Filters.command, test))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, build_add))
    dispatcher.add_handler(
        MessageHandler(Filters.command, get_help))
    updater.start_polling(poll_interval=1.0)
