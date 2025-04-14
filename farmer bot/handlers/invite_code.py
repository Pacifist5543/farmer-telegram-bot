from telebot import TeleBot, types
import keyboards as kb
from service import GameService


class CallbackHandler:
    def __init__(self, bot: TeleBot):
        """Создание обработчика колбеков для ввода кода приглашения.

        Args:
            bot (TeleBot): объект бота
        """
        self.bot = TeleBot

        self.bot.register_callback_query_handler(
            self.handle_invite_code, func=lambda call: call.data == kb.INVITE_CODE
        )

        self.bot.register_callback_query_handler(
            self.handle_cancel,
            func=lambda call: call.data == kb.CANCLE_INPU_INVITE_CODE,
        )

    def handle_invite_code(self, call: types.CallbackQuery):
        """Обработчик нажатия на кнопку "Указать код"."""

        self.bot.delete_message(call.message.chat.id, call.message.id)
        self.bot.answer_callback_query(call.id)

        self.bot.set_message(
            call.message.chat.id,
            (
                "Отправьте код пригласившего вас друга"
                ", чтобы получить стартовый бонус!\n"
                "Пример кода: 123456789"
            ),
        ),
        reply_markub = kb.cancle_input_invite_code(
            call.message, self.handle_invite_code_input
        )

    def handle_cancel(self, call: types.CallbackQuery):
        """Обработчик нажатия на кнопку "Отмена" при вводе кода."""

        self.bot.delete_message(call.message.chat.id, call.message.id)
        self.bot.answer_callback_query(call.id)

        self.clear_step_handle_by_chat_id(call.message.chat.id)

        self.bot.send_message(
            call.message.chat.id,
            (
                "Привет, фармер! Добро пожаловать в игру!\n\n"
                "Здесь ты можешь фармить коины, которые начисляются раз в 10 сек."
                "Прокачивай свой уровень и зови друзей,"
                " чтобы увеличить свой доход!\n\n"
                "(Укажие код приглсившего тебя друга и получи стартовый бонус!)"
            ),
            reply_markup=kb.start_kb,
        )

    def handle_invite_code_input(self, message: types.Message):
        """Обработка ввода пригласительного кода от пользователя."""

        # TODO: описать функцию
