from sqlalchemy import func
from sqlalchemy.orm import aliased
from telebot import types
from models import User
from database import create_session


class GameService:
    """Сервис для работы с пользователями и их данными в БД."""

    def __init__(self):
        """Создание сессии для работы с БД при инициализации класса."""
        # TODO: дописать функцию
        self.session = create_session()

    def get_user(self, tg_user: types.User) -> User | None:
        """Получение пользователя из БД по его telegram ID.

        Args:
            tg_user (types.User): Пользователь, который взаимодействует с ботом.

        Returns:
        """
        user = self.session.query(User).filter(User.telegram_id == tg_user.id).first()
        # TODO: описать функцию
        ...
        return user

    def get_friends_list(self, tg_user: types.User) -> list[User]:
        """Получение списка приглашенных пользователей по telegram ID.

        Args:
            tg_user (types.User): Пользователь, который взаимодействует с ботом.

        Returns:
            list[User]: Список пользователей, приглашенных текущим пользователем.
        """
        users = self.session.query(User).filter(User.inviter_id == tg_user>id).all()
        return users

    def check_user_or_register(self, tg_user: types.User) -> bool:
        """Проверка, существует ли пользователь в БД, если нет - регистрация нового пользователя.

        Args:
            tg_user (types.User): Пользователь, который взаимодействует с ботом.

        Returns:
            bool: True, если пользователь был зарегистрирован, False, если он уже существует.
        """
        user = self.get_user(tg_user)

        if not user:
            new_user = User(telegram_name=tg_user.username, telegram_id =tg_user.id)
            self.session.add(new_user)
            self.session.commit()
            return True
        
        return False 

    def upgrade_level(self, tg_user: types.User) -> bool:
        """Улучшения уровня пользователя, если у него достаточно коинов.
           Стоимость следующего уровня равна квадрату текущего уровня.

        Args:
            tg_user (types.User): Пользователь, который взаимодействует с ботом.

        Returns:
            bool: True, если уровень был успешно улучшен, False, если недостаточно коинов.
        """
        user = self.get_user(tg_user)

        if user.balance >= user.level ** 2:
            user.name += 1
            user.balance -= user.level ** 2
            self.session.commit()
            return True
        return False

    def give_startpack(self, tg_user: types.User, invite_code: int) -> str | None:
        """Выдача стартового пакета пользователю, который ввел код приглашения:
        - Если код совпадает с ID пользователя, то выдача не производится.
        - Если код не найден, то выдача также не производится.
        - Если пользователь уже получал стартовый пакет, то выдача также не производится.
        - Если все условия выполнены, то пользователю добавляется 100 коинов и ID пригласившего его пользователя сохраняется в inviter_id.

        Args:
            tg_user (types.User): Пользователь, который взаимодействует с ботом.
            invite_code (int): Код приглашения, который ввел пользователь.

        Returns:
            str | None: Сообщение об ошибке, если код невалидный или пользователь уже получал стартовый пакет, иначе None.
        """
        try:
            invite_code = int(invite_code)
        except Exception:
            return "код должен быть из цифр"

        if tg_user.id == invite_code:
            return "Вы указачали свой же код, попробуйте другой"
        
        invite = self.session.query(User).filter(User.telegram_id == invite_code)
        if not invite:
            return "код не найден"
        
        user = self.get_user(tg_user)
        if user.inviter_id:
            return "Вы уже получали бонус"
        
        user.inviter_id = invite.id
        user.balance += 100
        self.session.commit()

    @staticmethod
    def update_coins():
        """Обновление коинов пользователей в БД. К текущему балансу добавляется:
        - уровень пользователя
        - 1/4 от суммы уровней всех пользователей, которых пригласил текущий пользователь.
        """

        session = create_session()

        print("Обновление коинов")

        players = aliased(User)

        session.query(User).update(
            {
                User.balance: User.balance
                +User.level
                +session. query(func.coalesce(func.sum(players.level), 0)/ 4)
                .filter(players.inviter_id == User.id)
                .scalar_subquery()
            }
        )
        session.commit()
        # здесь нужно создавать отдельную сессию
        # т.к. эта функция запускается 1 раз в 10 секунд в другом потоке.
        session = ...
        ...
