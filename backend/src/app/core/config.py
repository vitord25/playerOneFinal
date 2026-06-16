"""Module used for reading values from the .env"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Ludoteca"

    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()