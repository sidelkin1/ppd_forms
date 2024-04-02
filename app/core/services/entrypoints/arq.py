from typing import Any, cast

from app.api.dependencies.path import PathProvider
from app.api.models.responses import (
    DatabaseResponse,
    ExcelResponse,
    FieldsResponse,
    MatrixResponse,
    OilLossResponse,
    ReportResponse,
    ReservoirsResponse,
)
from app.core.models.dto import UneftFieldDB, UneftReservoirDB
from app.core.services.entrypoints.registry import WorkRegistry
from app.core.services.matrix_report import matrix_report
from app.core.services.oil_loss_report import oil_loss_report
from app.core.services.opp_per_year_report import opp_per_year_report
from app.core.services.profile_report import profile_report
from app.infrastructure.holder import HolderDAO

registry = WorkRegistry()


@registry.add("excel:ns_ppd:refresh")
async def refresh_ns_ppd(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["file_local_dao"](path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_inj_loader.refresh()


@registry.add("excel:ns_ppd:reload")
async def reload_ns_ppd(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["file_local_dao"](path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_inj_loader.reload()


@registry.add("excel:ns_oil:refresh")
async def refresh_ns_oil(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["file_local_dao"](path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_oil_loader.refresh()


@registry.add("excel:ns_oil:reload")
async def reload_ns_oil(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["file_local_dao"](path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_oil_loader.reload()


@registry.add("excel:inj_db:refresh")
async def refresh_inj_db(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["file_local_dao"](path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.inj_well_database_loader.refresh()


@registry.add("excel:inj_db:reload")
async def reload_inj_db(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["file_local_dao"](path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.inj_well_database_loader.reload()


@registry.add("excel:neighbs:refresh")
async def refresh_neighbs(
    response: ExcelResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["file_local_dao"](path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.neighborhood_loader.refresh()


@registry.add("excel:neighbs:reload")
async def reload_neighbs(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["file_local_dao"](path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.neighborhood_loader.reload()


@registry.add("database:report:refresh")
async def refresh_mer(response: DatabaseResponse, ctx: dict[str, Any]) -> None:
    async with ctx["ofm_local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await holder.monthly_report_loader.refresh(
            date_from=response.task.date_from,
            date_to=response.task.date_to,
        )


@registry.add("database:report:reload")
async def reload_mer(response: DatabaseResponse, ctx: dict[str, Any]) -> None:
    async with ctx["ofm_local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await holder.monthly_report_loader.reload(
            date_from=response.task.date_from,
            date_to=response.task.date_to,
        )


@registry.add("database:profile:refresh")
async def refresh_opp(response: DatabaseResponse, ctx: dict[str, Any]) -> None:
    async with ctx["ofm_local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await holder.well_profile_loader.refresh(
            date_from=response.task.date_from,
            date_to=response.task.date_to,
        )


@registry.add("report:profile")
async def create_profile_report(
    response: ReportResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    async with ctx["local_pool_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await profile_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.well_profile_reporter,
            ctx["pool"],
            ctx["settings"],
        )


@registry.add("report:oil_loss:first_rate")
async def create_first_rate_loss_report(
    response: OilLossResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    async with ctx["local_pool_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await oil_loss_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.first_rate_loss_reporter,
            ctx["pool"],
            ctx["settings"],
        )


@registry.add("report:oil_loss:max_rate")
async def create_max_rate_loss_report(
    response: OilLossResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    async with ctx["local_pool_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await oil_loss_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.max_rate_loss_reporter,
            ctx["pool"],
            ctx["settings"],
        )


@registry.add("report:opp_per_year")
async def create_opp_per_year_report(
    response: ReportResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    async with ctx["ofm_pool_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await opp_per_year_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.opp_per_year_reporter,
            ctx["pool"],
            ctx["settings"],
        )


@registry.add("report:matrix")
async def create_matrix_report(
    response: MatrixResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    async with ctx["local_pool_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await matrix_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            response.task.base_period,
            response.task.pred_period,
            response.task.excludes,
            response.task.on_date,
            holder.matrix_reporter,
            ctx["pool"],
            ctx["settings"],
        )


@registry.add("uneft:fields")
async def get_fields(
    response: FieldsResponse, ctx: dict[str, Any]
) -> list[UneftFieldDB]:
    async with ctx["ofm_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        results = await holder.ofm_field_list.get_by_params()
    return results


@registry.add("uneft:reservoirs")
async def get_reservoirs(
    response: ReservoirsResponse, ctx: dict[str, Any]
) -> list[UneftReservoirDB]:
    async with ctx["ofm_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        results = await holder.ofm_reservoir_list.get_by_params(
            field_id=response.task.field_id
        )
    return results
