from enum import Enum


class TaskId(str, Enum):
    database = "database"
    report = "report"
    excel = "excel"
    uneft = "uneft"
