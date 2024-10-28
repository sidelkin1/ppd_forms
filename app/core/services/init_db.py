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


async def init_gtm_replace(
    dao: initializers.GtmReplaceInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_inj_well_database(
    dao: initializers.InjWellDatabaseInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_neighborhood(
    dao: initializers.NeighborhoodInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_new_strategy_inj(
    dao: initializers.NewStrategyInjInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_new_strategy_oil(
    dao: initializers.NewStrategyOilInitializer,
) -> None:
    await dao.initialize()
    await dao.commit()


async def init_well_test(dao: initializers.WellTestInitializer) -> None:
    await dao.initialize()
    await dao.commit()
