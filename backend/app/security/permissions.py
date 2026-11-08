"""
ACREVIA - Security Roles & Authorization Constants.
"""

from enum import Enum


class SystemRole(str, Enum):
    FARMER = "FARMER"
    AGRICULTURAL_EXPERT = "AGRICULTURAL_EXPERT"
    RESEARCHER = "RESEARCHER"
    ADMIN = "ADMIN"


class FarmRole(str, Enum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    WORKER = "WORKER"
    AGRONOMIST_ADVISOR = "AGRONOMIST_ADVISOR"
