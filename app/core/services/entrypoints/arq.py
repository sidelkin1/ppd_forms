from typing import Any, cast

from app.api.dependencies.path import PathProvider
from app.api.models.responses import (
    CompensationResponse,
    DatabaseResponse,
    ExcelResponse,
    FieldsResponse,
    FnvResponse,
    InjLossResponse,
    MatbalResponse,
    MatrixResponse,
    MmbResponse,
    OilLossResponse,
    ProlongResponse,
    ReportResponse,
    ReservoirsResponse,
    WellsResponse,
    WellTestResponse,
)
from app.core.config.main import get_mmb_settings
from app.core.config.models.app import AppSettings
from app.core.models.dto import UneftFieldDB, UneftReservoirDB, UneftWellDB
from app.core.services.entrypoints.registry import WorkRegistry
from app.core.services.reports import (
    compensation_report,
    fnv_report,
    inj_loss_report,
    matbal_report,
    matrix_report,
    mmb_report,
    oil_loss_report,
    opp_per_year_report,
    profile_report,
    prolong_report,
    well_test_report,
)
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


@registry.add("excel:gdis:refresh")
async def refresh_gdis(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](file_path=path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.well_test_loader.refresh()


@registry.add("excel:gdis:reload")
async def reload_gdis(response: ExcelResponse, ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    async with ctx["local_dao"](file_path=path) as holder:
        holder = cast(HolderDAO, holder)
        await holder.well_test_loader.reload()


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
            path_provider.dir_path(user_id, file_id),
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
            path_provider.dir_path(user_id, file_id),
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
            path_provider.dir_path(user_id, file_id),
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
            path_provider.dir_path(user_id, file_id),
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
            path_provider.dir_path(user_id, file_id),
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
            path_provider.dir_path(user_id, file_id),
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
            path_provider.dir_path(user_id, file_id),
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


@registry.add("report:prolong")
async def create_prolong_report(
    response: ProlongResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    path = path_provider.upload_dir(user_id)
    holder = HolderDAO(file_path=path / response.task.expected)
    csv_config: CsvSettings = ctx["csv_config"]
    await prolong_report(
        path_provider.dir_path(user_id, file_id),
        holder.excel_prolong_expected,
        path / response.task.actual,
        response.task.interpolation,
        ctx["pool"],
        csv_config,
    )


@registry.add("report:mmb")
async def create_mmb_report(
    response: MmbResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    app_config: AppSettings = ctx["app_config"]
    csv_config: CsvSettings = ctx["csv_config"]
    mmb_config = get_mmb_settings()
    async with ctx["ofm_dao"](path=path) as holder:
        holder = cast(HolderDAO, holder)
        await mmb_report(
            path_provider.dir_path(user_id, file_id),
            response.task.alternative,
            holder.mmb_reporter,
            ctx["pool"],
            app_config.delimiter,
            csv_config,
            mmb_config,
        )


@registry.add("report:compensation")
async def create_compensation_report(
    response: CompensationResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    csv_config: CsvSettings = ctx["csv_config"]
    async with ctx["ofm_dao"]() as holder:
        holder = cast(HolderDAO, holder)
        await compensation_report(
            path_provider.dir_path(user_id, file_id),
            response.task.on_date,
            holder.compensation_reporter,
            csv_config,
        )


@registry.add("report:well_test")
async def create_well_test_report(
    response: WellTestResponse, ctx: dict[str, Any]
) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    user_id = cast(str, response.job.user_id)
    file_id = cast(str, response.job.file_id)
    path = path_provider.upload_dir(user_id) / response.task.file
    app_config: AppSettings = ctx["app_config"]
    async with ctx["local_dao"](
        path=path, delimiter=app_config.delimiter
    ) as holder:
        holder = cast(HolderDAO, holder)
        await well_test_report(
            path_provider.dir_path(user_id, file_id),
            path_provider.data_dir / "well_test_template.xlsx",
            response.task.gtm_period,
            holder.well_test_reporter,
            ctx["pool"],
        )


@registry.add("uneft:fields")
async def get_fields(
    response: FieldsResponse, ctx: dict[str, Any]
) -> UneftFieldDB | list[UneftFieldDB] | None:
    app_config: AppSettings = ctx["app_config"]
    async with ctx["ofm_redis_dao"](expires=app_config.keep_result) as holder:
        holder = cast(HolderDAO, holder)
        results = await uneft_fields(
            response.task.stock, response.task.field_id, holder.uneft
        )
    return results


@registry.add("uneft:reservoirs")
async def get_reservoirs(
    response: ReservoirsResponse, ctx: dict[str, Any]
) -> list[UneftReservoirDB]:
    app_config: AppSettings = ctx["app_config"]
    async with ctx["ofm_redis_dao"](expires=app_config.keep_result) as holder:
        holder = cast(HolderDAO, holder)
        results = await uneft_reservoirs(response.task.field_id, holder.uneft)
    return results


@registry.add("uneft:wells")
async def get_wells(
    response: WellsResponse, ctx: dict[str, Any]
) -> list[UneftWellDB]:
    app_config: AppSettings = ctx["app_config"]
    async with ctx["ofm_redis_dao"](expires=app_config.keep_result) as holder:
        holder = cast(HolderDAO, holder)
        results = await uneft_wells(
            response.task.stock, response.task.field_id, holder.uneft
        )
    return results
