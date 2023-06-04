# -*- coding: utf-8 -*-
# pylint: disable=import-error
import logging

# методы IOgram для телеграмм
from aiogram import Bot, Dispatcher, executor, types

# Кастомные логи для телеграмм
from Logger import logger
# конфиги необходимые
from funcs import config_loader as cfg

# загрузка базового логгинга (можно менять уровень
# логов info, debag, errors, warnings)
logging.basicConfig(level=logging.INFO)

# Для работы бота в телеграмм
TOKEN = cfg.get_ntf_token()
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
    await message.answer('Бот оповещения о билдах')


async def send_build_info(message: str, build_info: str, finish: bool = False):
    """Отправка статуса билда в канал

    :param finish: флаг завершения отслеживания
    :param build_info: Номер билда и джоба для привязки сообщений
    :param message: Текст, отправляемый в телеграм-канал"""
    if not finish:
        await BOT.send_message(chat_id=CHAT_ID,
                               text=message,
                               parse_mode='MarkdownV2')
        TRACKING_BUILDS[build_info] = types.Message.message_id
    else:
        await BOT.send_message(chat_id=CHAT_ID,
                               text=message,
                               parse_mode='MarkdownV2',
                               reply_to_message_id=TRACKING_BUILDS[build_info])
        TRACKING_BUILDS.pop(build_info)


# Стартовая функция для запуска бота.
def tlg_ntf_thread():
    logger.info('Начало прослушки и готовности ботом принимать '
                'команды (long polling)')
    executor.start_polling(DP, skip_updates=True)
