from typing import Annotated

from pydantic import BaseModel, ConfigDict, conint, constr
from pydantic_settings import BaseSettings


class AbstractSettings(BaseSettings):
    class Config:
        env_file = ".env"


Password = Annotated(
    str,
    constr(
        min_length=6,
        pattern="^[A-Za-z0-9!@#$&*_+%-=]+$",
    ),
)

PhoneNumber = Annotated(
    str,
    constr(min_length=11, max_length=11),
)

CoopInt = Annotated(int, conint(ge=0))


class AbstractModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class AbstractResponse(BaseModel):
    status: int
