from app.api.dependencies.tasks.database import TaskDatabaseDep  # noqa
from app.api.dependencies.tasks.database import (
    create_task_database,
    task_database_provider,
)
from app.api.dependencies.tasks.excel import TaskExcelDep  # noqa
from app.api.dependencies.tasks.excel import (
    create_task_excel,
    task_excel_provider,
)
from app.api.dependencies.tasks.report import TaskReportDep  # noqa
from app.api.dependencies.tasks.report import (
    create_task_report,
    task_report_provider,
)
