---
name: new-report
description: Step-by-step guide for implementing a new PPD report in this codebase. Use whenever the user asks to add a new report, create a report endpoint, generate Excel/CSV reports, or mentions report templates, querysets, or ARQ worker registration. Covers API contract, data layer, service/entrypoint, frontend, iterative refinement, and test coverage.
---

# New Report Implementation

Follow these 6 steps to add a new report. Replace `<report>` with the lowercase report name throughout.

## Budget per step

| Step | Layer Group | What you build |
|------|-------------|----------------|
| 1. API contract | Enum → Schema → DTO → Response → Endpoint | Typed request/response, validation, route registration |
| 2. Data | Queryset → Reporter → Holder | SQL queries + DAO wired into the service locator |
| 3. Service + Entrypoint | Service → ARQ Registry | Business logic + background worker dispatch |
| 4. Frontend | YAML → Jinja2 → JS | HTML form for parameter input |
| 5. Refinement | Iterate as needed | Additional params, templates, enums |
| 6. Quality | Tests + mocks + fixtures | Integration tests with mock DAOs |

---

## Step 1. API Contract

Goal: API accepts a request and returns a typed response.

### Create

#### `app/core/models/schemas/<report>_params.py`

Pydantic model for input parameters. Always use `extra="forbid"`:

```python
from pydantic import BaseModel, ConfigDict

from app.core.models.dto import UneftFieldDB, UneftReservoirDB


class XxxParams(BaseModel):
    field: UneftFieldDB
    reservoir: UneftReservoirDB
    well: str

    model_config = ConfigDict(extra="forbid")
```

#### `app/core/models/dto/tasks/<report>.py`

Task DTO. Inherits `TaskReport` (which provides `name: ReportName` and a `filename_prefix` property) with `task_id` and `route_fields`:

```python
from datetime import date

from app.core.models.dto.db.field_list import UneftFieldDB
from app.core.models.dto.db.reservoir_list import UneftReservoirDB
from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import TaskId


class TaskXxx(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    field: UneftFieldDB
    reservoir: UneftReservoirDB
    well: str
    date_from: date
    date_to: date
```

Key contract: `route_fields=["task_id", "name"]` → `route_url = "report:xxx"` → matches `@registry.add("report:xxx")` in Step 3.

> `TaskId` does **not** need a new value — all reports reuse `task_id=TaskId.report`.
>
> `TaskReport` provides `name: ReportName` (auto-populated — do **not** redeclare in subclass) and a `filename_prefix` property (defaults to `self.name.value`). Override `filename_prefix` for custom file naming, e.g. `TaskOwcResp` returns `"{field}_{reservoir}_{well}"`. The prefix propagates to `JobStamp.prefix` → `file_id` via `ReportResponse.propagate_prefix`.

> Validation lives **only** in the Schema layer — DTOs trust pre-validated data. Common patterns:
> - `Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True)]` — normalize strings
> - `PositiveFloat`, `PositiveInt` — type-level constraints
> - `@field_validator("well", mode="after")` — custom single-field transforms
> - `@model_validator(mode="after")` — cross-field checks (e.g. date ordering)
>
> See `app/core/models/schemas/owc_resp_params.py` and `matrix_effect.py` for full examples.

### Edit

- **`app/core/models/enums/report_name.py`** — add value:
  ```python
  xxx = "xxx"
  ```

- **`app/core/models/dto/__init__.py`** — add import:
  ```python
  from .tasks.xxx import TaskXxx
  ```

- **`app/core/models/schemas/__init__.py`** — add import:
  ```python
  from .xxx_params import XxxParams
  ```

- **`app/api/models/responses/task.py`** — add Response type:
  ```python
  XxxResponse = ReportResponse[dto.TaskXxx]
  ```

- **`app/api/models/responses/__init__.py`** — add export:
  ```python
  from .task import XxxResponse
  ```

- **`app/api/endpoints/report.py`** — add endpoint.

    > **Note:** The catch-all `POST /{name}` endpoint accepts **only** a report name (no parameters) — it creates `TaskReport(name=name)`. Most reports need custom parameters and require a dedicated endpoint like the one below. See existing dedicated endpoints (`/profile`, `/opp_per_year`, `/matrix`, `/owc_resp`, etc.) for reference.

    Add imports at top:
    ```python
    from app.api.models.responses import XxxResponse
    from app.core.models.dto import TaskXxx
    from app.core.models.enums import ReportName
    from app.core.models.schemas import XxxParams
    ```

    Add route:
    ```python
    @router.post(
        "/xxx",
        status_code=status.HTTP_201_CREATED,
        response_model=XxxResponse,
        response_model_exclude_none=True,
    )
    async def generate_xxx_report(
        params: XxxParams,
        user: UserDep,
        redis: RedisDep,
        job: NewJobDep,
    ):
        task = TaskXxx(
            name=ReportName.xxx,
            field=params.field,
            reservoir=params.reservoir,
            well=params.well,
            date_from=params.date_from,
            date_to=params.date_to,
        )
        response = XxxResponse(task=task, job=job)
        await redis.enqueue_task(response, user.username)
        return response
    ```

---

## Step 2. Data

Goal: query data from OFM (Oracle) or local PostgreSQL via SQLAlchemy selects wrapped in a Reporter DAO.

### Create

#### `app/infrastructure/db/dao/sql/reporters/querysets/<report>/__init__.py`

Exports `select_*` functions from submodules:

```python
from .properties import select_properties
```

#### `app/infrastructure/db/dao/sql/reporters/querysets/<report>/properties.py`

SQLAlchemy `Select` returning data for one DataFrame:

```python
from sqlalchemy import bindparam, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import WellHdr, ...


def select_properties() -> Select:
    return select(
        bindparam("field_id").label("field_id"),
        bindparam("well").label("well"),
        WellHdr.well_name.label("branch"),
        ...
    ).where(
        WellHdr.uwi == ...,
        ...
    )
```

Rules:
- One function → one DataFrame
- Multiple data sets (e.g. properties + depths) → one file per query
- Use `bindparam("...")` for parameters passed from the service
- Table models for data from OFM (Oracle) come from `app.infrastructure.db.models.ofm.reflected`
- Table models for data from local PostgreSQL come from `app.infrastructure.db.models.local`

> Helper queries (e.g. `select_well_branch`, `select_water_density`) can live in separate files inside the same `querysets/<report>/` package and be imported by the main query file.

#### `app/infrastructure/db/dao/sql/reporters/<report>.py`

Reporter class mapping keys to queries. Extends `OfmBaseDAO`:

```python
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import xxx


class XxxReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "props": xxx.select_properties(),
            },
            pool,
        )
```

Local reporter extends `LocalBaseDAO`:

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.dao.sql.reporters.local import LocalBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import xxx


class XxxReporter(LocalBaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__({"props": xxx.select_properties()}, pool)
```

### Edit

- **`app/infrastructure/db/dao/sql/reporters/__init__.py`** — add export:
  ```python
  from .xxx import XxxReporter
  ```

- **`app/infrastructure/holder.py`** — add `@property`. Choose the pool based on data source:
  ```python
  # For OFM (Oracle) reporters:
  @property
  def xxx_reporter(self) -> db_reporters.XxxReporter:
      return db_reporters.XxxReporter(self.kwargs["ofm_pool"])


  # For local (PostgreSQL) reporters:
  @property
  def xxx_reporter(self) -> db_reporters.XxxReporter:
      return db_reporters.XxxReporter(self.kwargs["local_pool"])
  ```

    > Some reporters compose multiple DAOs (e.g. `matbal_reporter` combines `db_matbal_reporter` + `file_matbal_reporter`). Study existing properties in `holder.py` for complex patterns.

---

## Step 3. Service + Entrypoint

Goal: business logic and ARQ worker registration.

### Create

#### `app/core/services/reports/<report>.py`

Async function with business logic:

```python
from pathlib import Path
from shutil import make_archive

from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.sql.reporters import XxxReporter


async def xxx_report(
    path: Path,
    field_id: int,
    reservoir_id: int,
    well: str,
    dao: XxxReporter,
    pool: ProcessPoolManager,
) -> None:
    dfs = await dao.read_all(
        field_id=field_id, reservoir_id=reservoir_id, well=well
    )
    dfs["props"].to_excel(path / "xxx.xlsx")
    make_archive(str(path), "zip", root_dir=path)
```

> For single-file reports you may return the file directly without `make_archive`.

For Excel with a template:

```python
import openpyxl
from openpyxl.writer.excel import save_workbook


def _fill_calculator(ws, props):
    ws["B1"].value = props["field"].item()
    ...


def _process_calculator(dfs, path, template):
    wb = openpyxl.load_workbook(template)
    _fill_calculator(wb["Sheet1"], dfs["props"])
    save_workbook(wb, path / template.name)
    wb.close()
```

For parallel template writing:

```python
import asyncio

async with asyncio.TaskGroup() as tg:
    tg.create_task(pool.run(_process_calculator, dfs, path, template1))
    tg.create_task(pool.run(_process_analytics, dfs, path, template2))
make_archive(str(path), "zip", root_dir=path)
```

### Edit

- **`app/core/services/reports/__init__.py`** — add import:
  ```python
  from .xxx import xxx_report
  ```

- **`app/core/services/entrypoints/arq.py`** — register handler.
  Add imports:
  ```python
  from app.api.models.responses import XxxResponse
  from app.core.services.reports import xxx_report
  ```

  Add handler:
  ```python
  @registry.add("report:xxx")
  async def create_xxx_report(
      response: XxxResponse, ctx: dict[str, Any]
  ) -> None:
      path_provider: PathProvider = ctx["path_provider"]
      user_id = cast(str, response.job.user_id)
      file_id = cast(str, response.job.file_id)
      async with ctx["ofm_dao"]() as holder:
          holder = cast(HolderDAO, holder)
          await xxx_report(
              path_provider.dir_path(user_id, file_id),
              response.task.field.id,
              response.task.reservoir.id,
              response.task.well,
              holder.xxx_reporter,
              ctx["pool"],
          )
  ```

  If Excel templates are needed:
  ```python
  await xxx_report(
      ...
      path_provider.data_dir / "xxx_template.xlsx",
      ...
  )
  ```

> **DAO context**: pick the right context manager from `ctx` based on data sources:
> - `ctx["local_dao"]()` — PostgreSQL-only reports (e.g. `profile`, `inj_loss`, `matrix`)
> - `ctx["ofm_dao"]()` — Oracle-only reports (e.g. `opp_per_year`, `fnv`, `matbal`, `owc_resp`)
> - `ctx["ofm_local_dao"]()` — mixed reports (e.g. `well_test`)
> - `ctx["ofm_redis_dao"]()`, `ctx["local_dao"]()`, etc. — for other combinations

---

## Step 4. Frontend

Goal: HTML form for parameter input in the web interface.

### Edit

> Naming conventions:
> - Jinja2 macro: `form_xxx` where `xxx` is the report path, e.g. `form_owc_resp`
> - JS loader function: `loadXxx` in camelCase derived from report path, e.g. `loadOwcResp`

#### `app/api/config/yaml/reports.yaml`

Add a section for the report form. Simple fields as strings, dropdowns as arrays:

```yaml
- title: Report display title (Russian)
  path: xxx
  # ... form fields (field, reservoir, well, etc.) ...
  my_param: Parameter label
  my_select:
  - text: --Select--
    value: --
    selected: true
  - text: Option 1
    value: option_1
  description: Report description (shown below the form)
```

#### `app/templates/reports/macros/forms.html`

Each form is a Jinja2 macro with signature `(report, button_text, button_func)`. The macro must end with `{{ spinner_button(report.path, button_text, button_func) }}` to render the submit button with loading spinner. Import shared macros at the top of the file:

```html
{% from "/macros/forms.html" import date_range, spinner_button %}

{% macro form_xxx(report, button_text, button_func) %}
```

HTML markup for new fields. ID format: `{report.path}{PascalCase}`:

```html
<!-- input[number] -->
<div class="form-floating mb-3">
    <input type="number" class="form-control" id="{{ report.path }}MyParam"
           name="my_param" placeholder>
    <label for="{{ report.path }}MyParam">Parameter label</label>
</div>

<!-- select with cascade fetch -->
<select class="form-select mb-3" id="{{ report.path }}Fields"
        onchange="fetchReservoirs('{{ report.path }}', 'reservoirs')">
    {% for option in report.fields %}
        <option value="{{ option.value }}"
                {% if option.selected %}selected{% endif %}>
            {{ option.text }}
        </option>
    {% endfor %}
</select>

<!-- plain select -->
<select class="form-select mb-3" id="{{ report.path }}MySelect">
    {% for option in report.my_select %}
        <option value="{{ option.value }}"
                {% if option.selected %}selected{% endif %}>
            {{ option.text }}
        </option>
    {% endfor %}
</select>

<!-- file input -->
<div class="mb-3">
    <label class="form-check-label" for="{{ report.path }}Wells">{{ report.wells }}</label>
    <input type="file" class="form-control" id="{{ report.path }}Wells" name="file"/>
</div>

<!-- input[date] -->
<div class="form-floating mb-3">
    <input type="date" class="form-control" id="{{ report.path }}OnDate"
           name="on_date" placeholder>
    <label for="{{ report.path }}OnDate">As of date</label>
</div>

{{ spinner_button(report.path, button_text, button_func) }}
{% endmacro %}
```

#### `app/static/javascript/reports/load.js`

JS function to collect fields and send the request:

```javascript
async function loadXxx(reportName) {
  const fieldSelect = document.getElementById(`${reportName}Fields`);
  const field = fieldSelect.selectedOptions[0];
  const reservoir = document.getElementById(`${reportName}Reservoirs`).selectedOptions[0];
  const well = document.getElementById(`${reportName}Well`).value;
  const myParam = document.getElementById(`${reportName}MyParam`).value;
  const mySelect = document.getElementById(`${reportName}MySelect`).value;
  const onDate = document.getElementById(`${reportName}OnDate`).value;

  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const url = `/reports/${reportName}`;
  const data = {
    field: { id: parseInt(field.value), name: field.text },
    reservoir: { id: parseInt(reservoir.value), name: reservoir.text },
    well: well,
    my_param: myParam,
    my_select: mySelect,
    on_date: onDate,
  };

  const result = await assignWork(reportName, url, data);
  if (result) {
    await checkStatus(
      reportName,
      result.job.job_id,
      `/reports/${result.job.file_id}/zip`,
    );
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}
```

If the report requires file uploads (e.g. wells list):

```javascript
async function loadXxx(reportName) {
  const wellsFile = document.getElementById(`${reportName}Wells`).files[0];

  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const files = await sendReportFiles(reportName, [wellsFile], "/excel/");
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      wells: files[0] ? files[0].filename : null,
    };
    const result = await assignWork(reportName, url, data);
    if (result) {
      await checkStatus(
        reportName,
        result.job.job_id,
        `/reports/${result.job.file_id}/zip`,
      );
    }
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}
```

---

## Step 5. Refinement

Iterative step. Common patterns:

### Adding a new parameter

1. **Schema** — new field with validation in `<report>_params.py`
2. **DTO** — new field in `TaskXxx`
3. **Endpoint** — pass `params.xxx` into `TaskXxx(...)`
4. **Service** — use in calculations
5. **Queryset** — if new DB data needed, add `bindparam` or a new query
6. **Frontend** — field in `forms.html` + collection in `load.js` + label in `reports.yaml`

### Adding an Excel template/sheet

1. Place `.xlsx` template in `data_dir`
2. Service — fill function `_fill_xxx(ws, df)` + call `_process_xxx`
3. Entrypoint — pass `path_provider.data_dir / "template.xlsx"` to service
4. If >1 sheet — use `asyncio.TaskGroup` for parallel save

### Adding a new enum

1. Create/extend enum in `app/core/models/enums/`
2. Add field to Schema, DTO, Endpoint
3. Add `<select>` in forms (yaml + html + js)

---

## Step 6. Quality

Goal: tests, mocks, fixtures.

### Create

#### `tests/mocks/reporters.py` — mock Reporter

Add a stub class:

```python
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters import XxxReporter


class XxxMock(XxxReporter):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        pass

    async def read_all(self, **params) -> dict[str, pd.DataFrame]:
        return {
            "props": pd.DataFrame({
                "field": ["TestField"],
                "well": [params.get("well", "TEST")],
                ...
            }),
        }
```

#### `tests/mocks/holder.py` — mock HolderDAO

Add property:

```python
@property
def xxx_reporter(self):
    return XxxMock(self.kwargs["ofm_pool"])
```

#### `tests/fixtures/task_fixtures.py` — Schema + Task fixtures

Add both a schema fixture (for API request body) and a task fixture (for expected response):

```python
@pytest.fixture
def xxx():
    return XxxParams(
        field=FIELD,
        reservoir=RESERVOIR,
        well="TEST",
    )


@pytest.fixture
def task_xxx():
    return TaskXxx(
        name=ReportName.xxx,
        field=FIELD,
        reservoir=RESERVOIR,
        well="TEST",
    )
```

> Use shared constants `FIELD = UneftFieldDB(id=1, name="F1")` and `RESERVOIR = UneftReservoirDB(id=1, name="R1")` already defined in the fixtures file.

### Edit

#### `tests/integration/api/test_reports.py` — API endpoint test

```python
@pytest.mark.parametrize("task", ["task_xxx"])
async def test_generate_xxx_report(client, task, request, arq_redis):
    xxx = request.getfixturevalue("xxx")
    task_report = request.getfixturevalue(task)
    resp = await client.post(
        "/api/v1/reports/xxx", json=xxx.model_dump(mode="json")
    )
    assert resp.is_success
    data = resp.json()
    assert data["task"] == task_report.model_dump(
        mode="json", exclude_none=True
    )
```

#### `tests/integration/test_reports.py` — service test

```python
async def test_xxx_report(..., process_pool):
    await xxx_report(path, field_id, reservoir_id, well, mock_dao, process_pool)
    assert (path / "xxx.zip").exists()
```

#### `tests/integration/api/conftest.py` — register fixtures

```python
from tests.fixtures.task_fixtures import xxx, task_xxx
```

---

## Commit order

```
1. feat(report): add xxx report endpoint          ← Step 1
2. feat(report): add xxx report data layer        ← Step 2
3. feat(report): generate xxx xlsx report         ← Step 3
4. feat(report): add xxx frontend form            ← Step 4
5. feat(report): add Y to xxx report              ← Step 5 (optional iteration)
6. fix(report): address code review findings      ← Step 6a
7. test(reports): update xxx report fixtures      ← Step 6b
```

---

## File map

Legend: ✚ create, ✎ edit.

```
app/
├── api/
│   ├── config/yaml/reports.yaml              ✎
│   ├── endpoints/report.py                   ✎
│   └── models/responses/
│       ├── __init__.py                       ✎
│       └── task.py                           ✎
├── core/
│   ├── models/
│   │   ├── dto/
│   │   │   ├── __init__.py                   ✎
│   │   │   └── tasks/<report>.py             ✚
│   │   ├── enums/
│   │   │   └── report_name.py                ✎
│   │   └── schemas/
│   │       ├── __init__.py                   ✎
│   │       └── <report>_params.py            ✚
│   └── services/
│       ├── entrypoints/arq.py                ✎
│       └── reports/
│           ├── __init__.py                   ✎
│           └── <report>.py                   ✚
├── infrastructure/
│   ├── db/dao/sql/reporters/
│   │   ├── __init__.py                       ✎
│   │   ├── <report>.py                       ✚
│   │   └── querysets/<report>/
│   │       ├── __init__.py                   ✚
│   │       └── properties.py                 ✚
│   └── holder.py                             ✎
├── static/javascript/reports/load.js         ✎
└── templates/reports/macros/forms.html       ✎

tests/
├── fixtures/task_fixtures.py                 ✎
├── integration/
│   ├── api/
│   │   ├── conftest.py                       ✎
│   │   └── test_reports.py                   ✎
│   └── test_reports.py                       ✎
└── mocks/
    ├── holder.py                             ✎
    └── reporters.py                          ✎
```

---

## Important conventions

- **`route_fields` determines dispatch**: `route_fields=["task_id", "name"]` with `name=ReportName.xxx` produces `route_url = "report:xxx"` which matches `@registry.add("report:xxx")` in the ARQ worker.
- **DTOs inherit `TaskReport`**, not `TaskBase`. `TaskReport` provides `name: ReportName` and `filename_prefix` (default: `self.name.value`). Override `filename_prefix` for custom file naming (e.g. `TaskOwcResp` overrides it to `"{field}_{reservoir}_{well}"`).
- **`ReportResponse`** (not `BaseResponse`) is used for all report response aliases. Its `propagate_prefix` validator copies `task.filename_prefix` → `job.prefix` → `file_id`.
- **`OfmBaseDAO`** in `app/infrastructure/db/dao/sql/reporters/ofm.py` is the base class for OFM reporters. Study an existing reporter (e.g. `profile.py`, `matbal.py`) before implementing.
- **`HolderDAO`** in `app/infrastructure/holder.py` is the service locator. Each reporter needs a `@property` here.
- **Always read existing similar files before writing new ones** — mimic patterns for imports, naming, and structure.
- **Frontend ID convention**: `{report.path}{Suffix}` where `Suffix` starts with uppercase, e.g. `owc_respFields`, `profileWell`.
- Prefer `make_archive(str(path), "zip", root_dir=path)` for final output bundling.
