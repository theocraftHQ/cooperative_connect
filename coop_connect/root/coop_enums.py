from enum import Enum


class StrEnum(str, Enum):
    """Class a String Enum class that extends Enum."""

    def __str__(self):
        return str(self.value)


class CooperativeStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"  # They need to contact us or subscribe
    DEACTIVATED = "Deactivated"  # They no longer want to be with us


class CooperativeUserRole(StrEnum):
    PRESIDENT = "President"
    SECRETARY = "Secretary"
    TREASURER = "Treasurer"
    ACCOUNTANT = "Accountant"
    STAFF = "Staff"
    MEMBER = "Member"


class MembershipStatus(StrEnum):
    PENDING_APPROVAL = "Pending_approval"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"


class MembershipType(StrEnum):
    REGULAR = "Regular"
    CORPORATE = "Corporate"


class UserType(StrEnum):
    COOP_ADMIN = "Cooperative Admin"
    COOP_MEMBER = "Cooperative Member"
    ADMIN = "Admin"


class Gender(StrEnum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class UploadPurpose(StrEnum):
    SIGNATURE = "Signature"
    PASSPORT = "Passport"


class QuestionType(StrEnum):
    SHORT_TEXT = "Short_Text"
    LONG_TEXT = "Long_Text"
    SINGLE_CHOICE = "Single_Choice"
    MULTIPLE_CHOICE = "Multiple_Choice"
    DROPDOWN = "Dropdown"
    DATE = "Date"
    TIME = "Time"
    NUMBER = "Number"
    FILE_UPLOAD = "File_Upload"


class Environment(StrEnum):
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
