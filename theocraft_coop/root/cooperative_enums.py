from enum import Enum

class StrEnum(str, Enum):
    """Class a String Enum class that extends Enum."""

    def __str__(self):
        return str(self.value)
    
class CooperativeStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive" # They need to contact us or subscribe
    DEACTIVATED = "deactivated" # They no longer want to be with us

class CooperativeUserRole(StrEnum):
    PRESIDENT = "president"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    ACCOUNTANT = "accountant"
    STAFF = "staff"

class MembershipStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class MembershipType(StrEnum):
    REGULAR = "regular"
    CORPORATE = "corporate"