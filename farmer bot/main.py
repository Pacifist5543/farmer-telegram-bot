from telebot import TeleBot, types
import schedule
from threading import Thread
import time
import config
import keyboards as kb
from service import GameService
from handlers import invite_code, game
from database import create_all_table

import models  # это нужно, чтобы класс User создался и добавилсяв BaseModel.metadata

create_all_table()

bot = TeleBot(config.TOKEN)


def schedule_pending():
    """Запуск schedule для обновления коинов каждые 10 секунд.
    В этом потоке запускается функция update_coins из GameService, которая обновляет коинов у всех пользователей.
    """
    schedule.every(10).seconds.do(GameService.update_coins)
    while True:
        schedule.run_pending()
        time.sleep(1)
   

@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    register = GameService().check_user_or_register(message.from_user)

    if not register:
        bot.send_message(
            message.chat.id,
            "С возвращением!",
            reply_markup=kb.start_game_kb
        )
        return
    bot.send_message(
        message.chat.id,
        (
            "Привет, фармер! Добро пожаловать в игру!\n\n"
            "Здесь ты можешь фармить коины, которые начисляются раз в 10 сек."
            "Прокачивай свой уровень и зови друзей,"
            " чтобы увеличить свой доход!\n\n"
            "(Укажие код приглсившего тебя друга и получи стартовый бонус!)"
        ),
        reply_markup=kb.start_kb
    )


# обработка пригласительного кода
invite_code.CallbackHandler(bot)


# основные обработчики игры
game.CallbackHandler(bot)


# запуск потока для обновления коинов
Thread(target=schedule_pending).start()

print("Бот запущен")
bot.infinity_polling()
print("Бот выключут ")
