# -*- coding: utf-8 -*-
# pylint: disable=import-error
import asyncio
import logging

from aiogram import Bot, Dispatcher, executor, types

from Logger import logger
from funcs import config_loader as cfg
from funcs import main_funcs as mf

logging.basicConfig(level=logging.INFO)

TOKEN = cfg.get_token()
BOT = Bot(TOKEN)
DP = Dispatcher(BOT)
CHAT_ID = cfg.get_chat_id()
TRACKING_BUILDS = {}


@DP.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    """
    Запускается при первом запуске бота или при команде /start

    :param message: входящая команда /start
    """
    await message.answer('Бот контроля билдов активирован')


@DP.message_handler(commands=['test'])
async def test(message: types.Message) -> None:
    """
    Тестовая функция для отладки

    :param message: входящая команда /test
    """
    answer = mf.test_func()
    if answer:
        await message.answer(answer)
    else:
        await message.answer('Ничего не вернулось')


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


@DP.message_handler(commands=['build'])
async def build_add(message: types.Message) -> None:
    """
    Запуск нового билда на сборку

    :param message: входящая команда /build
    """
    answer = mf.add_build()
    await message.answer(answer)


# Прослушка сообщений
@DP.message_handler(content_types=['text'])
async def message_listener(message: types.Message) -> None:
    """
    Постоянная прослушка сообщений. В группах работает только при активной
    админке бота

    :param message: любой текст, отправляемый боту
    """
    pass


# Стартовая функция для запуска бота.
if __name__ == "__main__":
    logger.info('Начало прослушки и готовности ботом принимать '
                'команды (long polling)')
    executor.start_polling(DP, skip_updates=True)
