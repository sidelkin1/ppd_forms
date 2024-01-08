from .database import (
    DatabaseResponseDep,
    create_task_database,
    task_database_provider,
)
from .excel import ExcelResponseDep, create_task_excel, task_excel_provider
from .job import JobResponseDep, get_job_response, job_response_provider
from .oil_loss import (
    OilLossResponseDep,
    create_oil_loss_report,
    task_oil_loss_provider,
)
from .report import ReportResponseDep, create_task_report, task_report_provider
