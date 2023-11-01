from app.infrastructure.db.dao.complex import initializer


async def init_well_profile(dao: initializer.WellProfileInitializer) -> None:
    await dao.initialize()
    await dao.commit()


async def init_monthly_report(
    dao: initializer.MonthlyReportInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_field_replace(dao: initializer.FieldReplaceInitializer) -> None:
    await dao.initialize()
    await dao.commit()


async def init_reservoir_replace(
    dao: initializer.ReservoirReplaceInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_layer_replace(dao: initializer.LayerReplaceInitializer) -> None:
    await dao.initialize()
    await dao.commit()
