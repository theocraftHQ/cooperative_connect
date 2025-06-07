from enum import Enum


class StrEnum(str, Enum):
    """Class a String Enum class that extends Enum."""

    def __str__(self):
        return str(self.value)


class UserType(StrEnum):
    member = "Member"
    coop_admin = "Cooperative Admin"
    coop_member = "Cooperative Member"
    admin = "Admin"
