from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TypeVar, cast

from app.core.config.main import get_mmb_settings
from app.core.context import WorkerContext
from app.core.models.dto import UneftFieldDB, UneftReservoirDB, UneftWellDB
from app.core.models.responses import (
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
    OppPerYearResponse,
    OwcRespResponse,
    ProfileResponse,
    ProlongResponse,
    ReservoirsResponse,
    WellsResponse,
    WellTestResponse,
)
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
    owc_resp_report,
    profile_report,
    prolong_report,
    well_test_report,
)
from app.core.services.uneft import uneft_fields, uneft_reservoirs, uneft_wells
from app.infrastructure.db.dao.complex import loaders
from app.infrastructure.db.dao.complex import reporters as complex_reporters
from app.infrastructure.db.dao.complex.uneft import UneftDAO
from app.infrastructure.db.dao.sql import ofm
from app.infrastructure.files.dao import excel
from app.infrastructure.files.dao import reporters as file_reporters

registry = WorkRegistry()

T = TypeVar("T")


def _upload_path(ctx: WorkerContext, response: ExcelResponse) -> Path:
    return (
        ctx.paths.upload_dir(cast(str, response.job.user_id))
        / response.task.file
    )


def _ofm(reporter: T | None, name: str) -> T:
    if reporter is None:
        raise RuntimeError(f"OFM (Oracle) недоступен: {name}")
    return reporter


@asynccontextmanager
async def _uneft(ctx: WorkerContext) -> AsyncGenerator[UneftDAO, None]:
    with ctx.sessions.ofm_session() as session:
        async with ctx.sessions.redis_conn() as redis:
            yield UneftDAO(
                ofm.FieldListDAO(session, redis, ctx.settings.keep_result),
                ofm.ReservoirListDAO(session, redis, ctx.settings.keep_result),
                ofm.WellListDAO(session, redis, ctx.settings.keep_result),
            )


@registry.add("excel:ns_ppd:refresh")
async def refresh_ns_ppd(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.new_strategy_inj_loader(ctx.settings.delimiter)(
            session, _upload_path(ctx, response)
        )
        await loader.refresh()


@registry.add("excel:ns_ppd:reload")
async def reload_ns_ppd(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.new_strategy_inj_loader(ctx.settings.delimiter)(
            session, _upload_path(ctx, response)
        )
        await loader.reload()


@registry.add("excel:ns_oil:refresh")
async def refresh_ns_oil(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.new_strategy_oil_loader(
            session, _upload_path(ctx, response)
        )
        await loader.refresh()


@registry.add("excel:ns_oil:reload")
async def reload_ns_oil(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.new_strategy_oil_loader(
            session, _upload_path(ctx, response)
        )
        await loader.reload()


@registry.add("excel:inj_db:refresh")
async def refresh_inj_db(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.inj_well_database_loader(
            session, _upload_path(ctx, response)
        )
        await loader.refresh()


@registry.add("excel:inj_db:reload")
async def reload_inj_db(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.inj_well_database_loader(
            session, _upload_path(ctx, response)
        )
        await loader.reload()


@registry.add("excel:neighbs:refresh")
async def refresh_neighbs(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.neighborhood_loader(
            session, _upload_path(ctx, response)
        )
        await loader.refresh()


@registry.add("excel:neighbs:reload")
async def reload_neighbs(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.neighborhood_loader(
            session, _upload_path(ctx, response)
        )
        await loader.reload()


@registry.add("excel:gdis:refresh")
async def refresh_gdis(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.well_test_loader(session, _upload_path(ctx, response))
        await loader.refresh()


@registry.add("excel:gdis:reload")
async def reload_gdis(response: ExcelResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as session:
        loader = loaders.well_test_loader(session, _upload_path(ctx, response))
        await loader.reload()


@registry.add("database:report:refresh")
async def refresh_mer(response: DatabaseResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as local_session:
        with ctx.sessions.ofm_session() as ofm_session:
            loader = loaders.monthly_report_loader(local_session, ofm_session)
            await loader.refresh(
                date_from=response.task.date_from,
                date_to=response.task.date_to,
            )


@registry.add("database:report:reload")
async def reload_mer(response: DatabaseResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as local_session:
        with ctx.sessions.ofm_session() as ofm_session:
            loader = loaders.monthly_report_loader(local_session, ofm_session)
            await loader.reload(
                date_from=response.task.date_from,
                date_to=response.task.date_to,
            )


@registry.add("database:profile:refresh")
async def refresh_opp(response: DatabaseResponse, ctx: WorkerContext) -> None:
    async with ctx.sessions.local_session() as local_session:
        with ctx.sessions.ofm_session() as ofm_session:
            loader = loaders.well_profile_loader(local_session, ofm_session)
            await loader.refresh(
                date_from=response.task.date_from,
                date_to=response.task.date_to,
            )


@registry.add("report:profile")
async def create_profile_report(
    response: ProfileResponse, ctx: WorkerContext
) -> None:
    await profile_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.date_from,
        response.task.date_to,
        ctx.reporters.profile,
        ctx.process_pool,
        ctx.settings.delimiter,
    )


@registry.add("report:inj_loss:first_rate")
async def create_first_rate_inj_loss_report(
    response: InjLossResponse, ctx: WorkerContext
) -> None:
    await inj_loss_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.date_from,
        response.task.date_to,
        response.task.neighbs_from_ns_ppd,
        ctx.reporters.first_rate_inj_loss,
        ctx.process_pool,
        ctx.settings.delimiter,
    )


@registry.add("report:inj_loss:max_rate")
async def create_max_rate_inj_loss_report(
    response: InjLossResponse, ctx: WorkerContext
) -> None:
    await inj_loss_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.date_from,
        response.task.date_to,
        response.task.neighbs_from_ns_ppd,
        ctx.reporters.max_rate_inj_loss,
        ctx.process_pool,
        ctx.settings.delimiter,
    )


@registry.add("report:oil_loss:first_rate")
async def create_first_rate_oil_loss_report(
    response: OilLossResponse, ctx: WorkerContext
) -> None:
    await oil_loss_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.date_from,
        response.task.date_to,
        ctx.reporters.first_rate_oil_loss,
        ctx.process_pool,
    )


@registry.add("report:oil_loss:max_rate")
async def create_max_rate_oil_loss_report(
    response: OilLossResponse, ctx: WorkerContext
) -> None:
    await oil_loss_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.date_from,
        response.task.date_to,
        ctx.reporters.max_rate_oil_loss,
        ctx.process_pool,
    )


@registry.add("report:opp_per_year")
async def create_opp_per_year_report(
    response: OppPerYearResponse, ctx: WorkerContext
) -> None:
    await opp_per_year_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.date_from,
        response.task.date_to,
        _ofm(ctx.reporters.opp_per_year, "opp_per_year"),
        ctx.process_pool,
    )


@registry.add("report:matrix")
async def create_matrix_report(
    response: MatrixResponse, ctx: WorkerContext
) -> None:
    path = ctx.paths.upload_dir(cast(str, response.job.user_id))
    reporter = complex_reporters.MatrixReporter(
        ctx.reporters.matrix,
        file_reporters.MatrixReporter(path, response.task.wells),
    )
    await matrix_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.date_from,
        response.task.date_to,
        response.task.base_period,
        response.task.pred_period,
        response.task.excludes,
        response.task.on_date,
        reporter,
        ctx.process_pool,
        ctx.settings.delimiter,
    )


@registry.add("report:fnv")
async def create_fnv_report(response: FnvResponse, ctx: WorkerContext) -> None:
    await fnv_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.fields,
        response.task.min_radius,
        response.task.alternative,
        response.task.max_fields,
        _ofm(ctx.reporters.fnv, "fnv"),
    )


@registry.add("report:matbal")
async def create_matbal_report(
    response: MatbalResponse, ctx: WorkerContext
) -> None:
    path = ctx.paths.upload_dir(cast(str, response.job.user_id))
    reporter = complex_reporters.MatbalReporter(
        _ofm(ctx.reporters.matbal, "matbal"),
        file_reporters.MatbalReporter(
            path, response.task.wells, response.task.measurements
        ),
    )
    await matbal_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        ctx.paths.data_dir / "matbal_template.xlsm",
        response.task.field,
        response.task.reservoirs,
        response.task.alternative,
        reporter,
        ctx.process_pool,
    )


@registry.add("report:prolong")
async def create_prolong_report(
    response: ProlongResponse, ctx: WorkerContext
) -> None:
    path = ctx.paths.upload_dir(cast(str, response.job.user_id))
    await prolong_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        excel.ProlongExpectedDAO(path / response.task.expected),
        path / response.task.actual,
        response.task.interpolations,
        ctx.process_pool,
        ctx.csv,
    )


@registry.add("report:mmb")
async def create_mmb_report(response: MmbResponse, ctx: WorkerContext) -> None:
    path = (
        ctx.paths.upload_dir(cast(str, response.job.user_id))
        / response.task.file
    )
    reporter = complex_reporters.MmbReporter(
        _ofm(ctx.reporters.mmb, "mmb"),
        _ofm(ctx.reporters.mmb_alt, "mmb_alt"),
        file_reporters.MmbReporter(path),
    )
    await mmb_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.alternative,
        reporter,
        ctx.process_pool,
        ctx.settings.delimiter,
        ctx.csv,
        get_mmb_settings(),
    )


@registry.add("report:compensation")
async def create_compensation_report(
    response: CompensationResponse, ctx: WorkerContext
) -> None:
    await compensation_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        response.task.on_date,
        _ofm(ctx.reporters.compensation, "compensation"),
    )


@registry.add("report:well_test")
async def create_well_test_report(
    response: WellTestResponse, ctx: WorkerContext
) -> None:
    path = (
        ctx.paths.upload_dir(cast(str, response.job.user_id))
        / response.task.file
    )
    reporter = complex_reporters.WellTestReporter(
        ctx.reporters.well_test_local,
        file_reporters.WellTestReporter(path, ctx.settings.delimiter),
        _ofm(ctx.reporters.well_test_ofm, "well_test_ofm"),
    )
    await well_test_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        ctx.paths.data_dir / "well_test_template.xlsx",
        ctx.paths.data_dir / "well_test_arrow.png",
        response.task.gtm_period,
        response.task.gdis_period,
        response.task.radius,
        reporter,
        ctx.process_pool,
    )


@registry.add("report:owc_resp")
async def create_owc_resp_report(
    response: OwcRespResponse, ctx: WorkerContext
) -> None:
    await owc_resp_report(
        ctx.paths.dir_path(
            cast(str, response.job.user_id), response.job.file_id
        ),
        ctx.paths.data_dir / "owc_resp_template.xlsx",
        ctx.paths.data_dir / "analytics_template.xlsx",
        response.task.field,
        response.task.reservoir,
        response.task.well,
        response.task.pressure,
        response.task.depth,
        response.task.well_test,
        response.task.on_date,
        _ofm(ctx.reporters.owc_resp, "owc_resp"),
        ctx.process_pool,
    )


@registry.add("uneft:fields")
async def get_fields(
    response: FieldsResponse, ctx: WorkerContext
) -> UneftFieldDB | list[UneftFieldDB] | None:
    async with _uneft(ctx) as uneft:
        return await uneft_fields(
            response.task.stock, response.task.field_id, uneft
        )


@registry.add("uneft:reservoirs")
async def get_reservoirs(
    response: ReservoirsResponse, ctx: WorkerContext
) -> list[UneftReservoirDB]:
    async with _uneft(ctx) as uneft:
        return await uneft_reservoirs(response.task.field_id, uneft)


@registry.add("uneft:wells")
async def get_wells(
    response: WellsResponse, ctx: WorkerContext
) -> list[UneftWellDB]:
    async with _uneft(ctx) as uneft:
        return await uneft_wells(
            response.task.stock, response.task.field_id, uneft
        )
