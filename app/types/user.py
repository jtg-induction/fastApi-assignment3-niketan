from enum import Enum


class UserRole(str, Enum):
    OWNER = "OWNER"
    CUSTOMER = "CUSTOMER"
