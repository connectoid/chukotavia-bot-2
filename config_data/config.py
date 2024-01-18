import os
import dotenv
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    database_url: str         # Название базы данных
    db_host: str          # URL-адрес базы данных
    db_user: str          # Username пользователя базы данных
    db_password: str      # Пароль к базе данных


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    admin_id: int  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None = None) -> Config:

    dotenv.load_dotenv()

    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN'),
            admin_id=os.getenv('ADMIN_ID')
        ),
        db=DatabaseConfig(
            database_url=os.getenv('DATABASE_URL'),
            db_host=os.getenv('DB_HOST'),
            db_user=os.getenv('DB_USER'),
            db_password=os.getenv('DB_PASSWORD')
        )
    )
