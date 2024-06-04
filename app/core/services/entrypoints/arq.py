from typing import Any, cast

from app.api.dependencies.path import PathProvider
from app.api.models.responses import (
    DatabaseResponse,
    ExcelResponse,
    FieldsResponse,
    FnvResponse,
    InjLossResponse,
    MatbalResponse,
    MatrixResponse,
    OilLossResponse,
    ReportResponse,
    ReservoirsResponse,
    WellsResponse,
)
from app.core.config.models.app import AppSettings
from app.core.models.dto import UneftFieldDB, UneftReservoirDB, UneftWellDB
from app.core.services.entrypoints.registry import WorkRegistry
from app.core.services.fnv.report import fnv_report
from app.core.services.inj_loss_report import inj_loss_report
from app.core.services.matbal_report import matbal_report
from app.core.services.matrix_report import matrix_report
from app.core.services.oil_loss_report import oil_loss_report
from app.core.services.opp_per_year_report import opp_per_year_report
from app.core.services.profile_report import profile_report
from app.core.services.uneft import uneft_fields, uneft_reservoirs, uneft_wells
from app.infrastructure.files.config.models.csv import CsvSettings
from app.infrastructure.holder import HolderDAO

registry = WorkRegistry()


@registry.add("excel:ns_ppd:refresh")
async def refresh_ns_ppd(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    app_config: AppSettings = ctx["app_config"]
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](
        file_path=path, delimiter=app_config.delimiter
    ) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_inj_loader.refresh()


@registry.add("excel:ns_ppd:reload")
async def reload_ns_ppd(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    app_config: AppSettings = ctx["app_config"]
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](
        file_path=path, delimiter=app_config.delimiter
    ) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_inj_loader.reload()


@registry.add("excel:ns_oil:refresh")
async def refresh_ns_oil(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](file_path=path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_oil_loader.refresh()


@registry.add("excel:ns_oil:reload")
async def reload_ns_oil(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](file_path=path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.new_strategy_oil_loader.reload()


@registry.add("excel:inj_db:refresh")
async def refresh_inj_db(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](file_path=path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.inj_well_database_loader.refresh()


@registry.add("excel:inj_db:reload")
async def reload_inj_db(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](file_path=path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.inj_well_database_loader.reload()


@registry.add("excel:neighbs:refresh")
async def refresh_neighbs(
    response: ExcelResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](file_path=path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.neighborhood_loader.refresh()


@registry.add("excel:neighbs:reload")
async def reload_neighbs(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](file_path=path) as holder:
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
    app_config: AppSettings = ctx["app_config"]
    csv_config: CsvSettings = ctx["csv_config"]
    async with ctx["local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await profile_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.well_profile_reporter,
            ctx["pool"],
            app_config.delimiter,
            csv_config,
        )


@registry.add("report:inj_loss:first_rate")
async def create_first_rate_inj_loss_report(
    response: InjLossResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    app_config: AppSettings = ctx["app_config"]
    csv_config: CsvSettings = ctx["csv_config"]
    async with ctx["local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await inj_loss_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.first_rate_inj_loss_reporter,
            ctx["pool"],
            app_config.delimiter,
            csv_config,
        )


@registry.add("report:inj_loss:max_rate")
async def create_max_rate_inj_loss_report(
    response: InjLossResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    app_config: AppSettings = ctx["app_config"]
    csv_config: CsvSettings = ctx["csv_config"]
    async with ctx["local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await inj_loss_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.max_rate_inj_loss_reporter,
            ctx["pool"],
            app_config.delimiter,
            csv_config,
        )


@registry.add("report:oil_loss:first_rate")
async def create_first_rate_oil_loss_report(
    response: OilLossResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    csv_config: CsvSettings = ctx["csv_config"]
    async with ctx["local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await oil_loss_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.first_rate_oil_loss_reporter,
            ctx["pool"],
            csv_config,
        )


@registry.add("report:oil_loss:max_rate")
async def create_max_rate_oil_loss_report(
    response: OilLossResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    csv_config: CsvSettings = ctx["csv_config"]
    async with ctx["local_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await oil_loss_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.max_rate_oil_loss_reporter,
            ctx["pool"],
            csv_config,
        )


@registry.add("report:opp_per_year")
async def create_opp_per_year_report(
    response: ReportResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    csv_config: CsvSettings = ctx["csv_config"]
    async with ctx["ofm_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await opp_per_year_report(
            path_provider.file_path(user_id, file_id),
            response.task.date_from,
            response.task.date_to,
            holder.opp_per_year_reporter,
            ctx["pool"],
            csv_config,
        )


@registry.add("report:matrix")
async def create_matrix_report(
    response: MatrixResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    app_config: AppSettings = ctx["app_config"]
    csv_config: CsvSettings = ctx["csv_config"]
    async with ctx["local_dao"]() as holder:
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
            app_config.delimiter,
            csv_config,
        )


@registry.add("report:fnv")
async def create_fnv_report(
    response: FnvResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    async with ctx["ofm_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await fnv_report(
            path_provider.dir_path(user_id, file_id),
            response.task.fields,
            response.task.min_radius,
            response.task.alternative,
            response.task.max_fields,
            holder.fnv_reporter,
        )


@registry.add("report:matbal")
async def create_matbal_report(
    response: MatbalResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    path = path_provider.upload_dir(user_id)
    async with ctx["ofm_dao"](
        path=path,
        wells=response.task.wells,
        measurements=response.task.measurements,
    ) as holder:
        holder = cast(HolderDAO, holder)
        await matbal_report(
            path_provider.dir_path(user_id, file_id),
            path_provider.data_dir / "matbal_template.xlsm",
            response.task.field,
            response.task.reservoirs,
            response.task.alternative,
            holder.matbal_reporter,
            ctx["pool"],
        )


@registry.add("uneft:fields")
async def get_fields(
    response: FieldsResponse, ctx: dict[str, Any]
) -> UneftFieldDB | list[UneftFieldDB] | None:
    async with ctx["ofm_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        results = await uneft_fields(
            response.task.stock, response.task.field_id, holder.uneft
        )
    return results


@registry.add("uneft:reservoirs")
async def get_reservoirs(
    response: ReservoirsResponse, ctx: dict[str, Any]
) -> list[UneftReservoirDB]:
    async with ctx["ofm_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        results = await uneft_reservoirs(response.task.field_id, holder.uneft)
    return results


@registry.add("uneft:wells")
async def get_wells(
    response: WellsResponse, ctx: dict[str, Any]
) -> list[UneftWellDB]:
    async with ctx["ofm_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        results = await uneft_wells(
            response.task.stock, response.task.field_id, holder.uneft
        )
    return results
