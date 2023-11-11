from .database import TaskDatabase
from .excel import TaskExcel
from .holder import TaskHolderDTO
from .report import TaskReport

task_holder = TaskHolderDTO()
task_holder.add(TaskDatabase)
task_holder.add(TaskExcel)
task_holder.add(TaskReport)
