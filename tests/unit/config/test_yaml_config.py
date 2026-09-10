from typing import Any

from app.common.config.models.paths import Paths
from app.common.parsers import read_config, read_config_map
from app.core.models.enums import (
    ExcelTableName,
    ExcludeGTM,
    Interpolation,
    LossMode,
    OfmTableName,
    ReportName,
    WellTest,
)


def _assert_enum_coverage(
    values: set[str], enum_values: set[str], sentinels: set[str] | None = None
) -> None:
    """Значения опций (кроме UI-сентинелов) должны быть валидными enum."""
    allowed = (sentinels or {"--"}) | enum_values
    assert values <= allowed, f"не enum-значения: {values - allowed}"


def test_report_yaml_groups_valid(paths: Paths):
    config = read_config(paths.report_config)
    orders: list[int] = []
    for name, group in config["groups"].items():
        assert name
        assert group["icon"]
        assert group["color"]
        assert isinstance(group["order"], int)
        orders.append(group["order"])
    assert len(orders) == len(set(orders)), "дубль order у групп reports.yaml"


def test_report_yaml_items_valid(paths: Paths):
    config = read_config(paths.report_config)
    seen: set[str] = set()
    for report in config["items"]:
        assert report["title"]
        assert report["icon"]
        assert report["description"]
        assert report["group"] in config["groups"], report["path"]
        assert report["path"] not in seen, (
            f"дубль path у отчёта {report['path']}"
        )
        seen.add(report["path"])


def test_report_yaml_table_paths_valid(paths: Paths):
    reports = read_config(paths.report_config)["items"]
    tables = read_config(paths.table_config)["items"]
    table_paths = {table["path"] for table in tables}
    for report in reports:
        report_tables = report.get("tables")
        if not report_tables:
            continue
        required = report_tables.get("required") or []
        optional = report_tables.get("optional") or []
        assert isinstance(required, list), (
            f"{report['path']}: required не список"
        )
        assert isinstance(optional, list), (
            f"{report['path']}: optional не список"
        )
        assert not set(required) & set(optional), (
            f"{report['path']}: таблицы в required и optional дублируются"
        )
        for path in [*required, *optional]:
            assert path in table_paths, (
                f"{report['path']}: таблица {path!r} отсутствует в tables.yaml"
            )


def test_table_yaml_groups_valid(paths: Paths):
    config = read_config(paths.table_config)
    orders: list[int] = []
    for name, group in config["groups"].items():
        assert name
        assert group["icon"]
        assert group["color"]
        assert isinstance(group["order"], int)
        orders.append(group["order"])
    assert len(orders) == len(set(orders)), "дубль order у групп tables.yaml"


def test_table_yaml_items_valid(paths: Paths):
    config = read_config(paths.table_config)
    tables = config["items"]
    database_paths = {table.value for table in OfmTableName}
    excel_paths = {table.value for table in ExcelTableName}
    for table in tables:
        assert table["title"]
        assert table["path"]
        assert table["group"] in config["groups"], table["path"]
        assert isinstance(table["stale_after_days"], int)
        source = table["source"]
        assert source in {"database", "excel"}
        if source == "database":
            assert table["path"] in database_paths
        else:
            assert table["path"] in excel_paths


def test_mmb_yaml_valid(paths: Paths):
    config = read_config(paths.mmb_config)
    assert config["parameters"]
    for parameter in config["parameters"]:
        assert parameter["name"]
        assert parameter["min_value"] < parameter["max_value"]
        assert parameter["symbols"]
    press_tol = config["press_tol"]
    assert press_tol["min_value"] <= press_tol["max_value"]


def test_read_config_map(paths: Paths):
    tables = read_config_map(paths.table_config, "path")
    expected = {table.value for table in [*OfmTableName, *ExcelTableName]}
    assert set(tables) == expected
    assert tables["report"]["title"] == "МЭР"
    assert tables["gdis"]["stale_after_days"] == 60


def test_report_yaml_paths_match_report_name(paths: Paths):
    reports = read_config(paths.report_config)["items"]
    report_paths = {report["path"] for report in reports}
    assert report_paths == {name.value for name in ReportName}


def _option_values(report: dict[str, Any], field: str) -> set[str]:
    options = report.get(field, {}).get("options", [])
    return {option["value"] for option in options}


def test_report_yaml_enum_option_values(paths: Paths):
    reports = read_config_map(paths.report_config, "path")

    loss_values = {mode.value for mode in LossMode}
    for path in ("inj_loss", "oil_loss"):
        _assert_enum_coverage(
            _option_values(reports[path], "loss_mode"), loss_values
        )

    _assert_enum_coverage(
        _option_values(reports["prolong"], "interpolation"),
        {mode.value for mode in Interpolation},
        sentinels={"--", "all"},
    )

    _assert_enum_coverage(
        _option_values(reports["matrix"], "excludes"),
        {gtm.value for gtm in ExcludeGTM},
    )

    _assert_enum_coverage(
        _option_values(reports["owc_resp"], "well_test"),
        {test.value for test in WellTest},
    )
