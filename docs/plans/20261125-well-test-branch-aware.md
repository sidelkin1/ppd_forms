# Учет ствола скважины в отчете well_test

## Overview
Добавить в отчет по ГДИС определение ствола скважины по открытым перфорациям OFM. Для
текущего исследования ствол сохраняется в `WellTestResult`, для предыдущих исследований
выбирается по дате каждого замера. На листе `Лист1` вместо базового номера скважины
выводится ствол, а на листе `отчет` остаются только исследования текущего ствола с
прежним отображением номера скважины. Столбец `M` больше не заполняется; график
использует даты и давления из столбцов `D-E`.

## Context
- Files involved:
  - `app/core/models/dto/reports/well_test.py`
  - `app/infrastructure/db/dao/sql/reporters/ofm_well_test.py`
  - `app/infrastructure/db/dao/sql/reporters/querysets/well_test/__init__.py`
  - `app/infrastructure/db/dao/sql/reporters/querysets/well_test/branches.py` — новый запрос текущего ствола
  - `app/infrastructure/db/dao/sql/reporters/querysets/well_test/perfs.py` — новый запрос интервалов перфораций
  - `app/infrastructure/db/dao/complex/reporters/well_test.py`
  - `app/core/services/reports/well_test.py`
  - `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/branches.py` — условие открытого интервала вместо `BETWEEN` (правка уже внесена)
  - `tests/unit/reports/test_well_test.py` — новые unit-тесты
  - `tests/unit/reports/test_owc_resp_properties.py` — закрепить исправленное условие открытости в компилируемом SQL
  - `tests/mocks/reporters.py` — мок `OfmWellTestReporter` для теста оркестрации
  - `data/well_test_template.xlsx`
  - `docs/app/index.md`
- Related patterns:
  - Определение ствола на дату: `querysets/owc_resp/branches.py`.
  - Запрос перфораций и порядок их загрузки: `querysets/isobar/perfs.py`, `ofm_isobar.py`,
    `complex/reporters/isobar.py`.
  - Проверка интервалов `comp_date <= end_date` и `(close_date IS NULL OR close_date >= end_date)`: `reports/isobar/preparation.py`.
  - Резолв месторождения и объекта через справочник `DictG`: `querysets/isobar/perfs.py`
    (`_select_field_codes`, `_select_reservoir_layer_ids`, `common.cid_column`).
- Existing template state: в `data/well_test_template.xlsx` ряд `Pпл` уже ссылается на `отчет!D10:D55` и `отчет!E10:E55`,
  поэтому бинарный шаблон не требует изменения; нужно удалить программное заполнение
  `M` и закрепить ссылки графика тестом.
- Dependencies: новых пакетов не требуется. Используются существующие отраженные модели
  `WellHdr`, `WellPerforations`, `DictG`; полный набор integration-тестов требует Docker.

## Development Approach
- **Testing approach**: Regular — сначала небольшая реализация, затем unit-тесты соответствующего
  поведения.
- Выполнять задачи последовательно и не переходить к следующей, пока ее проверки не
  пройдены.
- OFM в unit-тестах заменять фейковыми DAO; реальное подключение к Oracle для
  автоматических проверок не требуется.
- Сохранять базовый номер скважины в `well`, а ствол передавать отдельно в `branch`, чтобы
  не смешивать ключи поиска и представление в двух листах Excel.
- **Единое правило выбора ствола** — лексикографический максимум имени. При общем коде
  месторождения `max(uwi)` совпадает с `max(well_name)` (`max(123, 123B1, 123B2) = 123B2`),
  поэтому выбор в SQL (Task 1) и в Python (Task 2) согласован. Исключение — многозначные
  суффиксы (`123B10` < `123B2`), оно принимается осознанно.
- **Ствол для истории несет суффикс пласта**: `branch` получает тот же суффикс ` (Пл)`,
  что и `well` истории; fallback при отсутствии перфораций — тоже `well` с суффиксом
  пласта.
- **Пустая история**: в тестах пустую историю задавать DataFrame с ожидаемыми колонками
  (включая `branch`); `_concat_tests` обязан сохранять колонки — при кадре без колонок
  `pd.DataFrame(results, columns=tests.columns)` даёт `(1, 0)`.
- **CRITICAL: every task MUST include new/updated tests**.
- **CRITICAL: all tests must pass before starting next task**.

## Implementation Steps

### Task 1: Получить ствол текущего ГДИС

**Files:**
- Modify: `app/core/models/dto/reports/well_test.py`
- Modify: `app/infrastructure/db/dao/sql/reporters/ofm_well_test.py`
- Modify: `app/infrastructure/db/dao/sql/reporters/querysets/well_test/__init__.py`
- Modify: `app/infrastructure/db/dao/complex/reporters/well_test.py`
- Modify: `app/infrastructure/db/dao/sql/reporters/querysets/owc_resp/branches.py` — условие открытого интервала вместо `BETWEEN` (правка уже внесена)
- Modify: `tests/unit/reports/test_owc_resp_properties.py` — закрепить новое условие в компилируемом SQL
- Create: `app/infrastructure/db/dao/sql/reporters/querysets/well_test/branches.py`
- Create: `tests/unit/reports/test_well_test.py`

- [x] Добавить обязательное поле `branch: str` в `WellTestResult`, оставив `well` базовым номером
  скважины.
- [x] Добавить запрос `branches`, который по имени месторождения, базовому номеру
  скважины, объекту и `end_date` находит ствол с открытой перфорацией и возвращает его
  `well_name` как `branch`. Резолв справочника — по образцу isobar, а не owc_resp: поле —
  через `DictG.description → id` (`_select_field_codes`), объект — через `mr`/ИЖВ-резолв
  `layer_id` (`_select_reservoir_layer_ids`), отображение объекта — `cid_column()`.
- [x] Учитывать открытые интервалы явным условием
  `comp_date <= :end_date AND (close_date IS NULL OR close_date >= :end_date)`;
  выбирать лексикографически максимальный ствол (`max(uwi)`); при отсутствии открытого
  ствола возвращать базовую скважину по аналогии с `owc_resp/branches.py` (`coalesce`).
- [x] В `owc_resp/branches.py` заменить `BETWEEN` тем же явным условием открытости и
  закрепить его проверкой в `test_owc_resp_properties` (правка кода уже внесена);
  существующие тесты owc_resp должны остаться зелёными.
- [x] Зарегистрировать запрос в `OfmWellTestReporter`; в `WellTestReporter.get_results` получать
  ствол для каждого результата параллельно (`asyncio.TaskGroup`, по одному запросу на
  пару «поле, скважина, объект, дата»), включая случай нескольких объектов у одного
  исследования.
- [x] Добавить unit-тесты на заполнение `branch`, разные стволы для разных объектов, fallback к
  базовой скважине и неизменность исходного `well`.
- [x] Добавить проверку компиляции запроса для Oracle: наличие всех параметров даты,
  месторождения, скважины и объекта, а также явного условия
  `close_date IS NULL OR close_date >= :end_date`. Определить в модуле собственный
  module-scope fixture с колонками `WellHdr`/`WellPerforations`/`DictG` (паттерн
  `test_owc_resp_properties.py`), не полагаясь на порядок исполнения модулей.
- [x] Запустить `uv run pytest tests/unit/reports/test_well_test.py`, затем полный `uv run pytest`; все тесты должны
  пройти перед Task 2.

### Task 2: Загрузить перфорации и определить стволы предыдущих ГДИС

**Files:**
- Modify: `app/infrastructure/db/dao/sql/reporters/ofm_well_test.py`
- Modify: `app/infrastructure/db/dao/sql/reporters/querysets/well_test/__init__.py`
- Modify: `app/infrastructure/db/dao/complex/reporters/well_test.py`
- Modify: `app/core/services/reports/well_test.py`
- Modify: `tests/unit/reports/test_well_test.py`
- Modify: `tests/mocks/reporters.py` — мок `OfmWellTestReporter` для теста оркестрации
- Create: `app/infrastructure/db/dao/sql/reporters/querysets/well_test/perfs.py`

- [x] Добавить запрос `perfs` с колонками `field`, `well`, `reservoir`, `branch`, `comp_date`, `close_date`, используя
  связь ствола с базовой скважиной (`coalesce(parent_uwi, uwi)`), резолв поля через
  `DictG.description → id` и фильтрацию объектов по образцу isobar (`mr`/ИЖВ-резолв).
  Параметр начала истории назвать `history_start` (не `previous_date`, чтобы не путать
  с квартальной семантикой isobar).
- [x] Загружать интервалы для базовой скважины текущего результата и всех его
  объектов, начиная с самой ранней даты предыдущих ГДИС; не отбрасывать еще открытые
  интервалы (`close_date IS NULL`) и интервалы, закрытые после начала истории
  (`close_date >= :history_start`).
- [x] Добавить полученные перфорации в результат `WellTestReporter.read_all`; для пустой истории
  возвращать пустой DataFrame с ожидаемыми колонками без лишнего запроса к OFM.
- [x] В сервисе well_test добавить резолв ствола отдельно для каждой строки по ключу
  месторождения, базовой скважины и объекта и по дате `end_date`.
- [x] При нескольких открытых стволах оставлять один с лексикографически максимальным
  именем (`123`, `123B1`, `123B2` → `123B2`) — то же правило, что `max(uwi)` в Task 1, —
  не размножая строку исследования.
- [x] Если открытой перфорации нет или таблица перфораций пуста, использовать
  базовый номер скважины с суффиксом пласта (как он приходит из истории); сохранять
  исходный порядок замеров и отображаемое значение `well`.
- [x] Обновить `_concat_tests`, чтобы предыдущие ГДИС получали рассчитанный `branch`, а текущие
  результаты сохраняли ствол из Task 1; `branch` для истории получает суффикс пласта;
  колонки (включая `branch`) сохраняются и при пустой истории.
- [x] Добавить unit-тесты на дату до/после закрытия интервала, открытый `close_date`, выбор
  `123B2` из нескольких стволов, отсутствие перфораций, пустую историю (кадр с
  ожидаемыми колонками, без `(1, 0)`), суффикс пласта у `branch` и отсутствие
  дублирования строк.
- [x] Добавить тест оркестрации `read_all` с моком `OfmWellTestReporter`
  (`tests/mocks/reporters.py`), проверяющий параметры загрузки перфораций и
  их наличие в наборе DataFrame.
- [x] Запустить `uv run pytest tests/unit/reports/test_well_test.py`, затем полный `uv run pytest`; все тесты должны
  пройти перед Task 3.

### Task 3: Изменить заполнение листов Excel и удалить заполнение столбца M

**Files:**
- Modify: `app/core/services/reports/well_test.py`
- Modify: `tests/unit/reports/test_well_test.py`

- [x] Перед записью диапазона `A-L` листа `Лист1` подставлять `branch` (с суффиксом пласта
  для истории, ствол текущего ГДИС — из Task 1) в столбец `B` для всех
  текущих и предыдущих ГДИС, не изменяя общий DataFrame и исходное поле `well`.
- [x] На листе `отчет` фильтровать историю одновременно по объекту и по `branch ==
  result["branch"]` до добавления строк ГТМ; текущий ГДИС должен всегда попадать на
  соответствующий лист. Строки ГТМ получают `branch = NaN` — это допустимо: фильтр
  применяется до их добавления, а в `B` у ГТМ пишется `well`; тесты это учитывают.
- [x] Оставить в столбце `B` листа `отчет` прежнее значение `well`; строки других стволов
  должны оставаться только на `Лист1`. Соседние ГДИС (секция `V-AC`) резолвом
  стволов не затрагиваются.
- [x] Удалить константу адреса `M9` и соответствующие элементы обеих конфигураций
  `_REPORT_TABLE_ROW_CELLS*`, чтобы в `M` не записывались ни давление, ни пустые значения, ни
  оформление строк.
- [x] Сохранить текущую логику границ дат и перемещения графика; ссылки ряда `Pпл`
  должны оставаться на столбцах `D-E`, без возврата источника из `M`.
- [x] Добавить регрессионный тест `_process_data` с реальным `data/well_test_template.xlsx`: проверить все
  строки и стволы на `Лист1`, отфильтрованную историю и базовый номер на `отчет`, пустой
  `M`, а также формулы `xVal`/`yVal` графика по `D-E`. Шаблон брать из `data/` в корне
  репозитория (например, фикстурой реальных шаблонов); fixture `paths` для этого не
  подходит — её `data_dir` указывает на `tests/fixtures/resources/data`.
- [x] Проверить сценарий без перфораций: оба листа используют базовую скважину (история —
  с суффиксом пласта), история не исчезает, а ГТМ продолжают добавляться по прежним
  правилам.
- [x] Запустить `uv run pytest tests/unit/reports/test_well_test.py`, затем полный `uv run pytest`; все тесты должны
  пройти перед Task 4.

### Task 4: Verify acceptance criteria

**Files:**
- Modify: `tests/unit/reports/test_well_test.py` — только если проверка выявит непокрытый сценарий

- [x] Запустить полный набор `uv run pytest` и убедиться, что существующие отчеты и
  integration-тесты не регрессировали. — 238 passed, 1 skipped.
- [x] Запустить `uv run ruff check app/ tests/`, `uv run ruff format --check app/ tests/` и `uv run mypy app/`.
  — ruff check чист при игнорировании EXE002 (артефакт прав монтирования: в git нет ни одного
  исполняемого файла, отслеживаемые режимы 644); ruff format — 477 files already formatted;
  mypy — Success: no issues found in 430 source files.
- [x] По автоматическим тестам подтвердить, что `Лист1!A-L` содержит все ГДИС со стволом
  в `B`, `отчет!B-J` содержит только текущий ствол с базовым номером в `B`, `M` не заполняется,
  а график строится по `D-E`. — `test_process_data_writes_branches_and_filters_report_sheet`
  и `test_process_data_without_perforations_uses_base_well` (реальный шаблон).

### Task 5: Update documentation

**Files:**
- Modify: `docs/app/index.md`

- [ ] Описать для отчета по ГДИС источник ствола, выбор последнего открытого ствола
  для предыдущих замеров (лексикографический максимум имени, с суффиксом пласта у
  истории) и различие между листами `Лист1` и `отчет`.
- [ ] Указать, что график давления использует столбцы `D-E`; общие инструкции README.md и
  архитектурные AGENTS.md/CLAUDE.md не менять, поскольку запуск и структура проекта не
  затрагиваются.
- [ ] Повторно запустить `uv run pytest tests/unit/reports/test_well_test.py` после завершения документации
  и убедиться, что проверки принятого поведения остаются успешными.
