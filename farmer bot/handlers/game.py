from telebot import TeleBot, types, apihelper
import keyboards as kb
from models import User
from service import GameService


class CallbackHandler:
    MAIN_TEXT = (
        "Ваши коины: {coins}\n\n"
        "Текущий доход коинов в 10 секунд: {level}\n"
        "Пассивный доход от друзей: {invited}\n\n"
        "[Стоимость следующего уровня: {price}]"
    )

    def __init__(self, bot: TeleBot):
        """Создание обработчика колбеков для основного функционала игры.

        Args:
            bot (TeleBot): объект бота
        """
        self.bot = bot

        self.bot.register_callback_query_handler(
            self.handle_main_menu,  # запускаем эту функцию
            func=lambda call: call.data
            == kb.START_GAME,  # если получили вот такой сигнал
        )
        self.bot.register_callback_query_handler(
            self.handle_update_info,  # запускаем эту функцию
            func=lambda call: call.data
            == kb.UPDATE_INFO,  # если получили вот такой сигнал
        )
        self.bot.register_callback_query_handler(
            self.handle_upgrade_level,  # запускаем эту функцию
            func=lambda call: call.data
            == kb.UPGRADE_LEVEL,  # если получили вот такой сигнал
        )
        self.bot.register_callback_query_handler(
            self.handle_friends_list,  # запускаем эту функцию
            func=lambda call: call.data
            == kb.FRIENDS_LIST,  # если получили вот такой сигнал
        )
        self.bot.register_callback_query_handler(
            self.handle_back_to_main,  # запускаем эту функцию
            func=lambda call: call.data
            == kb.BACK_TO_MAIN,  # если получили вот такой сигнал
        )

    def handle_main_menu(self, call: types.CallbackQuery):
        """Обработка главного игрового меню."""

        user = GameService().get_user(call.from_user)

        invited_players = GameService().get_friends_list(call.from_user)
        passive_income = sum([player.level for player in invited_players]) / 4

        self.bot.send_message(
            call.message.chat.id,
            text=self.MAIN_TEXT.format(
                coins=user.balance,
                level=user.level,
                invited=passive_income,
                price=user.level**2,
            ),
            reply_markup=kb.game_kb_main,
        )
        self.bot.answer_callback_query(call.id)

    def handle_update_info(self, call: types.CallbackQuery):
        """Обработка кнопки "обновить", которая редактирует главное меню, актуализируя данные."""

        user = GameService().get_user(call.from_user)

        invited_players = GameService().get_friends_list(call.from_user)
        passive_income = sum([player.level for player in invited_players]) / 4

        try:
            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text=self.MAIN_TEXT.format(
                    coins=user.balance,
                    level=user.level,
                    invited=passive_income,
                    price=user.level**2,
                ),
                reply_markup=kb.game_kb_main,
            )
        except apihelper.ApiTelegramException as e:
            pass
        self.bot.answer_callback_query(call.id)

    def handle_friends_list(self, call: types.CallbackQuery):
        """Отображение списка друзей и пригласительного года при нажатии на кнопку "список друзей"."""

        invited_players = GameService().get_friends_list(call.from_user)

        text = "У тебя нет друзей, выйди на улицу хотябы"

        if invited_players:
            text = "Ваши друзья:\n"
            for player in invited_players:
                text += f"@{player.telegram_name} - LVL {player.level}\n"

        text += f"\n\n[Ваш пригласительный код: {call.from_user.id}]"

        self.bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.id,
            reply_markup=kb.game_kb_back_to_main,
        )
        self.bot.answer_callback_query(call.id)

    def handle_back_to_main(self, call: types.CallbackQuery):
        """Возвращает пользователя в главное меню при нажатии кнопки "назад" в списке друзей."""
        self.handle_update_info(call)

    def handle_upgrade_level(self, call: types.CallbackQuery):
        """Обработка улучшения уровня на кпноку "повысить уровень"."""

        if not GameService().upgrade_level(call.from_user):
            self.bot.answer_callback_query(
                call.id, "Недостаточно коинов для прокачки уровня.", show_alert=True
            )
            return

        self.handle_update_info(call)

