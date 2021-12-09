from pydantic import BaseSettings


class APISettings(BaseSettings):
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_password: str
    mysql_user: str
    mysql_db: str
    redis_server: str = "127.0.0.1"
    redis_port: int = 6380
    redis_password: str

    max_wait_time_count: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
