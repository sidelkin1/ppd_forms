from app.infrastructure.db.dao.complex import initializers


async def init_well_profile(dao: initializers.WellProfileInitializer) -> None:
    await dao.initialize()
    await dao.commit()


async def init_monthly_report(
    dao: initializers.MonthlyReportInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_field_replace(
    dao: initializers.FieldReplaceInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_reservoir_replace(
    dao: initializers.ReservoirReplaceInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_layer_replace(
    dao: initializers.LayerReplaceInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()
