from enum import Enum

from app.crud.base import CRUDBase
from app.crud.monthly_report import crud_monthly_report
from app.crud.well_profile import crud_well_profile


class LoadMode(str, Enum):

    def __new__(cls, title: str, method: str):
        obj = str.__new__(cls, title)
        obj._value_ = title
        obj.method = method
        return obj

    REFRESH = ('refresh', 'refresh_local_database')
    RELOAD = ('reload', 'reload_local_database')

    def __call__(self, crud: CRUDBase):
        return getattr(crud, self.method)


class TableName(str, Enum):

    def __new__(cls, title: str, crud: CRUDBase):
        obj = str.__new__(cls, title)
        obj._value_ = title
        obj.crud = crud
        return obj

    REPORT = ('report', crud_monthly_report)
    PROFILE = ('profile', crud_well_profile)
