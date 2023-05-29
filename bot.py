# -*- coding: utf-8 -*-
# pylint: disable=import-error
import logging

# методы IOgram для телеграмм
from aiogram import Bot, Dispatcher, executor, types

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
TOKEN = cfg.get_token()
BOT = Bot(TOKEN)
DP = Dispatcher(BOT)
# то куда мы будем выводить, информация о билде
CHAT_ID = cfg.get_chat_id()
TRACKING_BUILDS = {}


# Стартовая функция
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
    Запуск нового билда на сборку (возможно расширение
    функции для указания конкретного билда)

    :param message: входящая команда /build
    """
    answer = mf.add_build()
    await message.answer(answer)


@DP.message_handler(commands=['help'])
async def get_help(message: types.Message) -> None:
    """
    Получение справки по боту

    :param message: входящая команда /help
    """
    answer = mf.get_help()
    if answer:
        await message.answer(answer)
    else:
        await message.answer('Ничего не вернулось')


# Стартовая функция для запуска бота.
if __name__ == "__main__":
    logger.info('Начало прослушки и готовности ботом принимать '
                'команды (long polling)')
    executor.start_polling(DP, skip_updates=True)
