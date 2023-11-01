from app.core.models.dto.tasks.database import TaskDatabase
from app.core.models.dto.tasks.excel import TaskExcel
from app.core.models.dto.tasks.holder import TaskHolderDTO
from app.core.models.dto.tasks.report import TaskReport

task_holder = TaskHolderDTO()
task_holder.add(TaskDatabase)
task_holder.add(TaskExcel)
task_holder.add(TaskReport)
