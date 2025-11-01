import functools
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_file: Path = Path(__file__).resolve().parent.parent.parent.joinpath("app")
    env_file: Path = app_file.joinpath(".env")

    keyboard_main: list[list[str]] = [
        ["Начать смену", "Закрыть смену", "Текущая смена"],
        ["Начать месяц", "Завершить месяц", "Текущий месяц"],
        ["Графики за смену", "Графики за месяц"],
    ]
    keyboard_ratio: list[list[str]] = [["Ставка 5%", "Ставка 10%"]]

    TOKEN: str = "token"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5555
    POSTGRES_USER: str = "pionflo-bot-db"
    POSTGRES_PASSWORD: str = "pionflo-bot-db"
    POSTGRES_DB: str = "pionflo-bot-db"

    @functools.cached_property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=env_file if env_file else None,
        env_file_encoding="utf-8",
        extra="allow",
    )


@functools.lru_cache()
def settings() -> Settings:
    return Settings()
