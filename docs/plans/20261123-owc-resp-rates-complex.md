# Расширение отчета owc_resp дебитами ТР/МЭР и сложными ГДИС

## Overview

Добавить в отчет `owc_resp` новый вид исследования `complex`, выгрузку актуальных дебитов и
забойного давления из технологических режимов (ТР) и МЭР, дополнительные PVT-свойства и
перфорации. Для сложных исследований расширить существующие Excel-отчеты и формировать
дополнительный файл на основе `rn_vega_template.xlsx`.

Состав Excel-файлов для `static_level`/`pressure` сохраняется. Единственное намеренное
изменение для всех видов ГДИС — обводненность `watercut` переводится на выбор источника
«ТР, если дата ТР больше или равна дате МЭР, иначе МЭР» (см. Уточнения).

## Context

- Основные файлы:
  - `app/core/models/enums/well_test.py`
  - `app/api/config/yaml/reports.yaml`
  - `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/`
  - `app/infrastructure/db/models/ofm/udmurtneft_n.py`
  - `app/core/services/reports/owc_resp.py`
  - `app/core/services/entrypoints/arq.py`
- Шаблоны:
  - `data/owc_resp_template.xlsx`
  - `data/analytics_template.xlsx`
  - `data/rn_vega_template.xlsx`
- Тесты:
  - `tests/unit/config/test_yaml_config.py`
  - `tests/integration/test_reports.py`
  - `tests/integration/api/test_reports.py`
  - `tests/fixtures/task_fixtures.py`
  - `tests/mocks/reporters.py`
- Related patterns:
  - выбор последней записи через `ROW_NUMBER` в `owc_resp/well_reservoir.py`;
  - объединение нефтяного и нагнетательного фонда с приоритетом источника в
    `querysets/isobar/stock.py`;
  - сопоставление пластов по идентификаторам и названиям в `querysets/matbal/resp.py`;
  - параллельное формирование Excel-файлов и упаковка в ZIP в `app/core/services/reports/owc_resp.py`.
- Dependencies: новых внешних зависимостей не требуется; используются SQLAlchemy, openpyxl и
  существующие отражаемые OFM-модели.
- Уточнения:
  - дебиты МЭР переводятся из часов в сутки с множителем `24`;
  - для нагнетательных скважин ТР `tr_watercut = 100`;
  - отсутствие записей ТР/МЭР не должно удалять строку свойств скважины;
  - для расчета плотности жидкости используется `reservoir_oil_density`, но в формулах
    аналитики используется `surface_oil_density`;
  - переопределение `watercut` на ТР-приоритетный выбор — намеренное изменение поведения для
    всех видов ГДИС: «ТР, если `tr_date >= mer_date`, иначе МЭР»;
  - ТР-таблицы `TmpWellOpOis2/TmpWellNgOis2.uwi` хранят базовый UWI (без суффикса ствола
    `B1`/`B2`), сопоставление — по `coalesce(WellHdr.parent_uwi, WellHdr.uwi)`.

## Предварительная верификация (до реализации)

SQL-запросы зависят от отражённых OFM-моделей (`DeferredReflection`), поэтому имена колонок
нельзя проверить по исходникам — их нужно подтвердить по схемам `udmurtneft_n`/`codes` до
начала Task 2–3. При расхождении скорректировать названия колонок в queryset'ах и в этом
плане.

Сверить по Oracle/OFM:

- `udmurtneft_n.well_month_hist`: `uwi`, `layer_id`, `start_date`, `oil`, `water`, `act_time`,
  `oil_v`, `water_v`.
- `udmurtneft_n.tmp_wellop_ois2`: `uwi`, `official_date`, `layer_id`, `oil_rate`, `liq_rate`,
  `water_cut`, `flow_pressure`.
- `udmurtneft_n.tmp_wellng_ois2`: `uwi`, `official_date`, `layer_id`, `intake`,
  `layer_flow_pressure`.
- `udmurtneft_n.well_perforations`: `top`, `base`, `comp_date`, `close_date`, `layer_id`, `uwi`.
- `udmurtneft_n.res_pty`: `initial_layer_pressure`, `bubble_point_pressure`, `gas_factor`,
  `layer_oil_dyn_viscosity`, `layer_water_dyn_viscosity`, `oil_compressibility`,
  `layer_oil_density`, `layer_temperature`, `layer_oil_compressibility`,
  `water_compressibility`, `separated_oil_density`, `water_density`, `abs_depth_owc`.
- `udmurtneft_n.well_hdr_pty`: `uwi`, `property_id`, `num_val` (для радиуса скважины
  `property_id == "1071381"`).
- `codes.dict_g`: `id`, `mr`, `description`, `code`.

⚠️ `oil_fvf` берётся из `res_pty.oil_compressibility` — в БД эта колонка названа
`OIL_COMPRESSIBILITY`, но фактически хранит объёмный коэффициент нефти (FVF). Наименование
в БД неверное, маппинг остаётся как в `plan.md`.

## Development Approach

- **Testing approach**: Regular — сначала реализация небольшого изменения, затем его тесты.
- Выполнять задачи последовательно и полностью завершать каждую перед переходом к
  следующей.
- SQL-запросы (`querysets/owc_resp/*`) опираются на отражённые OFM-модели и не поддаются
  unit-тестированию без Oracle; их проверка выполняется прогоном на данных OFM (см.
  «Предварительная верификация»). Excel и API расширяются существующими интеграционными
  тестами с mock DAO.
- Использовать различимые значения полей в mock-данных, чтобы тесты выявляли
  перепутанные SQL- и Excel-маппинги.
- **CRITICAL: every task MUST include new/updated tests** — для SQL-задач (Task 2–3) аналогом
  тестов служит прогон запросов на данных OFM (unit-тесты невозможны из-за `DeferredReflection`).
- **CRITICAL: all tests must pass before starting next task**

## Implementation Steps

### Task 1: Добавить вид исследования complex

**Files:**
- Modify: `app/core/models/enums/well_test.py`
- Modify: `app/api/config/yaml/reports.yaml`
- Modify: `tests/unit/config/test_yaml_config.py`

- [x] Добавить `WellTest.complex` и вариант `Сложное` в конфигурацию формы `owc_resp`.
- [x] Убедиться, что существующие `OwcRespParams` и `TaskOwcResp` принимают и сериализуют новое
  значение без новых полей задачи.
- [x] Добавить тест на наличие `complex` в YAML и соответствие значений `well_test` в YAML
  enum `WellTest`.
- [x] Запустить связанные unit-тесты и полный `uv run pytest`; все тесты должны пройти перед Task
  2.

### Task 2: Реализовать выбор дебитов ТР и МЭР

**Files:**
- Modify: `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/reservoirs.py`
- Create: `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/mer_rates.py`
- Create: `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/tr_rates.py`
- Create: `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/rates.py`

- [x] Добавить `select_reservoir_names()` с `lower(DictG.description)` для `DictG.id == reservoir_id` и
  `DictG.mr == to_char(reservoir_id)`.
- [x] В `mer_rates.py` сохранить фильтры по базовой скважине
  (`WellMonthHist.uwi == coalesce(WellHdr.parent_uwi, WellHdr.uwi)`), `select_reservoir_ids()` и
  последней дате `start_date <= on_date`; агрегировать записи выбранной даты до одной строки.
- [x] Рассчитать `mer_oil_rate = 24 * OIL / ACT_TIME` и `mer_liq_rate = 24 * объем_или_масса / ACT_TIME`;
  при отсутствии положительного суммарного `ACT_TIME` возвращать `NULL`, не допуская деления на
  ноль.
- [x] Для `mer_liq_rate` использовать суммы `OIL_V + WATER_V`, если объемная добыча больше нуля,
  иначе суммы `OIL + WATER`; для `mer_watercut` использовать соответствующее отношение с
  умножением на `100`, а при нулевых обоих знаменателях возвращать `100`.
- [x] В `tr_rates.py` объединить `TmpWellOpOis2` и `TmpWellNgOis2`; фильтровать по базовому UWI
  (`TmpWellOpOis2.uwi == coalesce(WellHdr.parent_uwi, WellHdr.uwi)` — базовый UWI без суффикса
  ствола), `official_date <= on_date` и `lower(layer_id).in_(select_reservoir_names())`.
- [x] Выбрать последнюю дату ТР, при равенстве дат дать приоритет нефтяному фонду;
  свести возможные дубликаты к одной строке с детерминированным выбором числовых
  значений.
- [x] Вернуть из ТР `tr_oil_rate`, `tr_liq_rate`, `tr_watercut` и `tr_bhp`; для нагнетательного фонда
  использовать `INTAKE`, `LAYER_FLOW_PRESSURE`, `tr_oil_rate = NULL` и `tr_watercut = 100`.
- [x] В `rates.py` выбрать источник между ТР и МЭР по правилу «более поздняя дата, при равенстве —
  ТР»: `CASE WHEN tr_date IS NOT NULL AND (mer_date IS NULL OR tr_date >= mer_date) THEN ТР ELSE МЭР`;
  сформировать `oil_rate`, `liq_rate`, `watercut` и независимо сохранить `tr_bhp` (только из ТР).
- [x] Обеспечить однострочный результат даже при отсутствии обоих источников; в этом
  случае итоговые дебиты, обводненность и `tr_bhp` должны быть `NULL`.
- [x] Прогнать запросы на данных OFM (skipped - not automatable: OFM требует Oracle thick client
  `libclntsh.so`, недоступный в окружении); форма запросов проверена компиляцией с диалектом Oracle
  (фильтры пластов и дат, множитель `24`, fallback объем/масса, `100` для нагнетательных, отсутствие
  `GROUP BY` и приоритеты источников).
- [x] Запустить полный `uv run pytest`; все тесты должны пройти перед Task 3.

### Task 3: Расширить итоговую SQL-выгрузку свойств

**Files:**
- Modify: `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/properties.py`
- Rename: `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/top_perf.py` → `perfs.py`
- Modify: `app/infrastructure/db/models/ofm/udmurtneft_n.py`
- Delete: `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/watercut.py`

- [x] Сохранить `select_top_perf()` (перенести в `perfs.py`) и добавить `select_bottom_perf()` через
  `MAX(WellPerforations.base)` с теми же фильтрами скважины, пласта и активности перфорации на
  `on_date`.
- [x] Подключить однострочный запрос `rates.py` к `properties` без потери строки при отсутствии
  ТР/МЭР; добавить в результат `oil_rate`, `liq_rate`, `watercut`, `tr_bhp` и `bottom_perf`.
- [x] Заменить импорт `select_watercut` из `watercut.py` на `rates.py`, после чего удалить
  `watercut.py`.
- [x] Переименовать `oil_density` в `surface_oil_density`.
- [x] Добавить из `ResPty` поля `init_resp`, `bubble_resp`, `gas_factor`, `oil_viscosity`, `water_viscosity`,
  `oil_fvf`, `reservoir_oil_density`, `reservoir_temperature`, `oil_compressibility` и `water_compressibility`;
  два последних умножить на `0.00001`. Исходные колонки — см. «Предварительная верификация»
  (в т.ч. `oil_fvf` берётся из `oil_compressibility`, несмотря на название).
- [x] Добавить `field_code` через `DictG.id == WellHdr.field`.
- [x] Добавить отражаемую модель `WellHdrPty` для `udmurtneft_n.well_hdr_pty` и скалярный `well_radius` по
  `property_id == "1071381"`; агрегировать возможные дубликаты, чтобы не нарушать однострочность
  результата.
- [x] Прогнать запрос на данных OFM (skipped - not automatable: Oracle thick client
  `libclntsh.so` недоступен); форма запроса проверена компиляцией с диалектом Oracle в
  `tests/unit/reports/test_owc_resp_properties.py` (все новые labels, join кода месторождения,
  фильтр радиуса, `MAX(base)`, множитель `0.00001`, cross join однострочной выгрузки дебитов без
  потери строки).
- [x] Запустить полный `uv run pytest`; все тесты должны пройти перед Task 4.

### Task 4: Обновить калькулятор и аналитический Excel-отчет

**Files:**
- Modify: `app/core/services/reports/owc_resp.py`
- Modify: `tests/mocks/reporters.py`
- Modify: `tests/integration/test_reports.py`

- [x] Разделить прежних потребителей `oil_density`: поверхностную плотность получать из
  `surface_oil_density`, пластовую — из `reservoir_oil_density`.
- [x] Заполнять `B12` калькулятора значением `reservoir_oil_density`; удалить перезапись `B15`,
  чтобы сохранить уже имеющуюся формулу `=B12*(1-B14/100)+B13*B14/100`.
- [x] В Python-расчете плотности жидкости использовать `reservoir_oil_density` и итоговую
  обводненность: `reservoir_oil_density * (1 - watercut / 100) + water_density * watercut / 100`.
- [x] В формулах аналитики использовать `surface_oil_density` через `AL5`, а не `reservoir_oil_density`; не
  подставлять в эти формулы плотность жидкости, рассчитанную по пластовой плотности
  нефти.
- [x] Для `complex` заполнить аналитику: `R5=tr_bhp`, `S5=oil_rate`, `T5=liq_rate`, `AE5=init_resp`,
  `AF5=bubble_resp`, `AG5=gas_factor`, `AH5=oil_viscosity`, `AI5=water_viscosity`, `AK5=oil_fvf`.
- [x] Для `complex` записать `AJ5="=AH5*(1-U5/100)+AI5*U5/100"` и оставить `BL5/BM5` пустыми.
- [x] Добавить запись ячейки `AX5` («Цель исс-ия») кодом: `"Рпл + ФЕС пласта"` для `complex`, `"Рпл"`
  для остальных (сейчас `AX5` — статичный дефолт шаблона и кодом не заполняется).
- [x] Для остальных видов ГДИС сохранить существующие значения и ветки static/pressure,
  включая заполнение `BL5/BM5`; ячейки, предназначенные только для complex, оставлять
  пустыми.
- [x] Во всех режимах заполнять `AL5=surface_oil_density`.
- [x] Расширить `OwcRespMock` всеми новыми свойствами различимыми значениями, обязательно
  различая `surface_oil_density` и `reservoir_oil_density`.
- [x] Обновить тесты калькулятора и аналитики: проверить формулу `B15`, использование
  пластовой плотности для расчета плотности жидкости и поверхностной плотности в
  формулах аналитики.
- [x] Запустить интеграционные тесты отчета и полный `uv run pytest`; все тесты должны
  пройти перед Task 5.

### Task 5: Формировать RN Vega для сложных исследований

**Files:**
- Modify: `app/core/services/reports/owc_resp.py`
- Modify: `app/core/services/entrypoints/arq.py`
- Modify: `tests/fixtures/task_fixtures.py`
- Modify: `tests/integration/api/test_reports.py`
- Modify: `tests/integration/api/conftest.py` при необходимости экспорта fixture
- Modify: `tests/integration/test_reports.py`

- [x] Передать `data/rn_vega_template.xlsx` из worker entrypoint в `owc_resp_report` и добавить
  обработчик заполнения RN Vega; выходной файл сохраняет имя шаблона `rn_vega_template.xlsx`.
- [x] Формировать и добавлять RN Vega в ZIP только для `WellTest.complex`; для static/pressure
  сохранить прежний состав архива.
- [x] На листе `Интерпретация` заполнить `C6=workshop`, `C7=field_code`, `C8=field`, `C9=pad`, `C10=reservoir`,
  `C11=well`, `C13=well_mode`, `C14=wellbore`, `C15=well_lift`, `C16=well_radius`, `C17=depth`.
- [x] Заполнить `C18` строкой `f"{top_perf}-{bottom_perf}"`, `C19=top_perf`, `C20=top_perf_offset`, `C23=elevation`,
  `C25=well_status`, `C27=tr_bhp`, `C28=liq_rate`, `C29=oil_rate`, `C30=watercut`, `C32=abs_depth_owc`.
- [x] Заполнить `C35=oil_compressibility`, `C36=water_compressibility`, `C38=init_resp`, `C39=reservoir_temperature`,
  `C41=bubble_resp`, `C42=gas_factor`, `C43=oil_viscosity`, `C44=water_viscosity`, `C46=oil_fvf`, `C49=surface_oil_density`,
  `C50=water_density`, `C51=reservoir_oil_density`, `C61=depth`, `C62=depth_offset`.
- [x] На листе `Давление` записать `A2=on_date` как дату Excel и `B2=pressure`; лист `Дебит` не
  изменять.
- [x] Добавить complex task fixture и API-тест успешной постановки задания; расширить workbook
  integration-тест проверками всех перечисленных ячеек и наличия RN Vega только в complex ZIP.
- [x] Проверить отсутствие RN Vega в legacy-режимах и неизменность листа `Дебит`.
- [x] Запустить API/report integration-тесты и полный `uv run pytest`.

### Task 6: Verify acceptance criteria

- [ ] Запустить полный набор тестов: `uv run pytest`.
- [ ] Запустить линтер: `uv run ruff check app/ tests/`.
- [ ] Проверить форматирование: `uv run ruff format --check app/ tests/`.
- [ ] Запустить проверку типов: `uv run mypy app/`.
- [ ] Проверить покрытие новых и измененных ветвей тестами не ниже 80%, включая
  complex/legacy, отсутствие дебитов (mock с NULL-дебитами/давлением) и раздельное
  использование пластовой/поверхностной плотности. SQL-логика ТР/МЭР покрывается прогоном
  на данных OFM, а не unit-тестами.
- [ ] Сверить итоговое поведение с `plan.md`: UI complex, все SQL-поля, оба обновленных шаблона и
  условное создание RN Vega.

### Task 7: Update documentation

- [ ] Проверить, что документация и тестовые команды соответствуют фактической реализации.
  `README.md` не перечисляет виды ГДИС и состав файлов `owc_resp` — правка не требуется.
- [ ] Обновить `AGENTS.md`/`CLAUDE.md` только если изменятся задокументированные внутренние
  соглашения; новых архитектурных паттернов не вводить.
