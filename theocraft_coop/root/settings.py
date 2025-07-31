from pydantic import EmailStr
from pydantic.networks import PostgresDsn

from .utils.base_schemas import AbstractSettings


class Settings(AbstractSettings):
    postgres_url: PostgresDsn
    jwt_secret_key: str
    ref_jwt_secret_key: str
    second_signer_key: str
    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_from_name: str
    mail_port: int
    mail_server: str
    sms_url: str
    sms_username: str
    sms_apikey: str
    app_name: str = "Theocraft Coop"


settings = Settings()
