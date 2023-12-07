from typing import Any, cast

from app.core.models.dto import JobStamp, TaskDatabase, TaskExcel, TaskReport
from app.core.services.entrypoints.registry import WorkRegistry
from app.core.services.oil_loss_report import oil_loss_report
from app.core.services.profile_report import profile_report
from app.core.utils.result_path import result_path
from app.infrastructure.holder import HolderDAO

registry = WorkRegistry()


@registry.add("excel:ns_ppd:refresh")
async def refresh_ns_ppd(
    task: TaskExcel, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["excel_local_dao"](task.path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_inj_loader.refresh()


@registry.add("excel:ns_ppd:reload")
async def reload_ns_ppd(
    task: TaskExcel, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["excel_local_dao"](task.path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_inj_loader.reload()


@registry.add("excel:ns_oil:refresh")
async def refresh_ns_oil(
    task: TaskExcel, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["excel_local_dao"](task.path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_oil_loader.refresh()


@registry.add("excel:ns_oil:reload")
async def reload_ns_oil(
    task: TaskExcel, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["excel_local_dao"](task.path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_oil_loader.reload()


@registry.add("excel:inj_db:refresh")
async def refresh_inj_db(
    task: TaskExcel, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["excel_local_dao"](task.path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.inj_well_database_loader.refresh()


@registry.add("excel:inj_db:reload")
async def reload_inj_db(
    task: TaskExcel, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["excel_local_dao"](task.path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.inj_well_database_loader.reload()


@registry.add("excel:neighbs:refresh")
async def refresh_neighbs(
    task: TaskExcel, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["excel_local_dao"](task.path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.neighborhood_loader.refresh()


@registry.add("excel:neighbs:reload")
async def reload_neighbs(
    task: TaskExcel, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["excel_local_dao"](task.path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.neighborhood_loader.reload()


@registry.add("database:report:refresh")
async def refresh_mer(
    task: TaskDatabase, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["ofm_local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await holder.monthly_report_loader.refresh(
            date_from=task.date_from, date_to=task.date_to
        )


@registry.add("database:report:reload")
async def reload_mer(
    task: TaskDatabase, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["ofm_local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await holder.monthly_report_loader.reload(
            date_from=task.date_from, date_to=task.date_to
        )


@registry.add("database:profile:refresh")
async def refresh_opp(
    task: TaskDatabase, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["ofm_local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await holder.well_profile_loader.refresh(
            date_from=task.date_from, date_to=task.date_to
        )


@registry.add("report:profile")
async def create_profile_report(
    task: TaskReport, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["local_pool_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await profile_report(
            result_path(job.user_id, job.file_id),
            task,
            holder.well_profile_reporter,
            ctx["pool"],
        )


@registry.add("report:oil_loss")
async def create_oil_loss_report(
    task: TaskReport, job: JobStamp, ctx: dict[str, Any]
) -> None:
    async with ctx["local_pool_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await oil_loss_report(
            result_path(job.user_id, job.file_id),
            task,
            holder.oil_loss_reporter,
            ctx["pool"],
        )
