const MS_PER_DAY = 86400000;

const STATUS = Object.freeze({
  STALE: "stale",
  FRESH: "fresh",
  UNKNOWN: "unknown",
});

document.addEventListener("DOMContentLoaded", () => {
  loadReportStaleness(reports, dbTables);
});

function staleStatus(maxDate, staleAfterDays) {
  if (maxDate === null || maxDate === undefined || maxDate === "") {
    return STATUS.STALE;
  }
  const stored = new Date(maxDate).getTime();
  if (!Number.isFinite(stored)) {
    return STATUS.UNKNOWN;
  }
  const now = new Date();
  const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  const days = (today - stored) / MS_PER_DAY;
  return days > staleAfterDays ? STATUS.STALE : STATUS.FRESH;
}

async function fetchTableDates(table) {
  try {
    const response = await fetchWithAuth(
      buildUrl(`/${table.source}/${table.path}`),
    );
    if (!response.ok) {
      return { table, status: STATUS.UNKNOWN };
    }
    const { max_date } = await response.json();
    return { table, status: staleStatus(max_date, table.stale_after_days) };
  } catch (error) {
    console.error(`Error fetching dates for ${table.title}:`, error);
    return { table, status: STATUS.UNKNOWN };
  }
}

function tableName(table) {
  return table.optional ? `${table.title} (необяз.)` : table.title;
}

function tooltipSection(title, names) {
  const items = names.map((name) => `<li>${name}</li>`).join("");
  return (
    `<strong>${title}</strong>` +
    `<ul class="mb-0 ps-3 text-start">${items}</ul>`
  );
}

async function updateReportCard(path, tablesToCheck) {
  const loader = document.getElementById(`${path}StalenessFetch`);
  const tipEl = document.getElementById(`${path}TablesTip`);
  if (!loader || !tipEl) {
    return;
  }
  loader.classList.remove("d-none");
  try {
    const results = await Promise.all(tablesToCheck.map(fetchTableDates));
    const staleNames = results
      .filter(({ status }) => status === STATUS.STALE)
      .map(({ table }) => tableName(table));
    const unknownNames = results
      .filter(({ status }) => status === STATUS.UNKNOWN)
      .map(({ table }) => tableName(table));
    const sections = [];
    if (staleNames.length) {
      sections.push(tooltipSection("Устарели:", staleNames));
    }
    if (unknownNames.length) {
      sections.push(tooltipSection("Не удалось проверить:", unknownNames));
    }
    tipEl.classList.toggle("d-none", sections.length === 0);
    const content = sections.join("");
    const tooltip = bootstrap.Tooltip.getInstance(tipEl);
    if (tooltip) {
      // title открывает show()-gate в Bootstrap (_isWithContent)
      // и задаёт содержимое при первом показе
      tooltip._config.title = content;
    }
  } catch (error) {
    console.error(`Error updating staleness for ${path}:`, error);
  } finally {
    loader.classList.add("d-none");
  }
}

function reportCheck(report, dbTables) {
  const required = report.tables.required || [];
  const optional = report.tables.optional || [];
  const tablesToCheck = [];
  for (const path of required) {
    if (dbTables[path]) {
      tablesToCheck.push({ ...dbTables[path], path, optional: false });
    }
  }
  for (const path of optional) {
    if (!required.includes(path) && dbTables[path]) {
      tablesToCheck.push({ ...dbTables[path], path, optional: true });
    }
  }
  return tablesToCheck;
}

async function loadReportStaleness(reports, dbTables) {
  try {
    await Promise.all(
      reports
        .filter((report) => report.tables)
        .map((report) =>
          updateReportCard(report.path, reportCheck(report, dbTables)),
        ),
    );
  } catch (error) {
    console.error("Error checking report staleness:", error);
  }
}
