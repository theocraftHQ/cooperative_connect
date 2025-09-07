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
    sms_apikey: str
    sms_username: str
    aws_access_key: str
    aws_secret_key: str
    aws_bucket: str
    aws_region_name: str
    app_name: str = "Coopconnnect"
    payaza_public_token: str
    payaza_secret_key: str

settings = Settings()
