/* Выгрузка ФНВ по нескольким месторождениям.
 *
 * Одно месторождение - одна задача воркера, поэтому UI сам создаёт
 * несколько запросов и следит за каждым по своему websocket. Прогресс,
 * сводный статус и отмена группы реализованы здесь; общие функции
 * (assignWork, waitJobTerminal, showFormAlert) берутся из core/.
 */

/* Статусы и цвета - только из палитры skills/ppd-colors (--ppd-*). */
const FNV_STATES = {
  queued: {
    icon: "bi-hourglass-split",
    badge: "ppd-badge-queued",
    iconClass: "ppd-icon-queued",
    label: "В очереди",
  },
  stopping: {
    icon: "bi-slash-circle",
    badge: "ppd-badge-queued",
    iconClass: "ppd-icon-queued",
    label: "Останавливается…",
  },
  completed: {
    icon: "bi-check-circle-fill",
    badge: "ppd-badge-done",
    iconClass: "ppd-icon-done",
    label: "Готово",
  },
  cancelled: {
    icon: "bi-slash-circle-fill",
    badge: "ppd-badge-cancelled",
    iconClass: "ppd-icon-cancelled",
    label: "Отмена",
  },
  error: {
    icon: "bi-x-circle-fill",
    badge: "ppd-badge-error",
    iconClass: "ppd-icon-error",
    label: "Ошибка",
  },
};

const FNV_TERMINAL = ["completed", "cancelled", "error"];

let fnvRunning = false;
let fnvCancelRequested = false;

function isFnvTerminal(job) {
  return FNV_TERMINAL.includes(job.state);
}

function collectFnvFields(name) {
  const select = document.getElementById(`${name}Fields`);
  return [...select.selectedOptions]
    .filter((opt) => opt.value !== "--")
    .map((opt) => ({ id: Number(opt.value), name: opt.text }));
}

function fnvAddFieldRow(name, job) {
  const state = FNV_STATES[job.state];
  const row = document.createElement("li");
  row.className =
    "list-group-item d-flex justify-content-between align-items-center px-0 py-1";

  const icon = document.createElement("i");
  icon.className = `bi ${state.icon} ${state.iconClass} me-2`;
  const label = document.createElement("span");
  label.appendChild(icon);
  label.appendChild(document.createTextNode(job.field.name));

  const status = document.createElement("span");

  row.appendChild(label);
  row.appendChild(status);
  document.getElementById(`${name}FieldList`).appendChild(row);

  job.iconNode = icon;
  job.statusNode = status;
  return job;
}

function fnvRenderState(job) {
  // после запроса отмена необработанные строки показываем как
  // останавливающиеся: итог придёт один, в сводном сообщении
  const view = job.stopping && !isFnvTerminal(job) ? "stopping" : job.state;
  const state = FNV_STATES[view];
  job.iconNode.className = `bi ${state.icon} ${state.iconClass} me-2`;
  const badge = document.createElement("span");
  badge.className = `badge ${state.badge} me-2`;
  // текст ошибки не показываем: он длинный, ломает строку и дублирует лог
  badge.textContent = state.label;
  job.statusNode.replaceChildren(badge);
  if (view !== job.state) {
    return;
  }
  // успех - архив точно есть, упавшее месторождение проверяем запросом:
  // задача могла упасть раньше отчёта и архива не оставить
  if (job.fileId && job.state === "completed") {
    job.statusNode.appendChild(fnvDownloadLink(job, "Скачать"));
  } else if (job.fileId && job.state === "error" && job.hasArchive) {
    job.statusNode.appendChild(fnvDownloadLink(job, "Скачать лог"));
  } else if (job.state === "error" && job.hasArchive === false) {
    const note = document.createElement("span");
    note.className = "text-muted small";
    note.textContent = "лог недоступен";
    job.statusNode.appendChild(note);
  }
}

function fnvDownloadLink(job, text) {
  const link = document.createElement("a");
  link.className = "alert-link";
  link.href = buildUrl(`/reports/${job.fileId}/zip`);
  link.textContent = text;
  return link;
}

async function fnvArchiveExists(job) {
  try {
    const response = await fetchWithAuth(
      buildUrl(`/reports/${job.fileId}/zip/exists`),
    );
    if (!response.ok) {
      return false;
    }
    const data = await response.json();
    return data.exists === true;
  } catch (error) {
    console.error(error);
    return false;
  }
}

function updateFnvProgress(name, jobs) {
  const total = jobs.length;
  const done = jobs.filter(isFnvTerminal).length;
  document.getElementById(`${name}ProgressLabel`).textContent =
    `Обработано ${done} из ${total}`;
  const bar = document.getElementById(`${name}ProgressBar`);
  bar.style.width = total ? `${Math.round((done / total) * 100)}%` : "0%";
  bar.classList.remove("ppd-bar-run", "ppd-bar-done", "ppd-bar-error");
  if (done === total && !jobs.some((job) => job.state === "error")) {
    bar.classList.add("ppd-bar-done");
  } else if (jobs.some((job) => job.state === "error")) {
    bar.classList.add("ppd-bar-error");
  } else {
    bar.classList.add("ppd-bar-run");
  }
}

async function fnvSendCancel(jobs) {
  const active = jobs.filter((job) => !isFnvTerminal(job));
  await Promise.all(
    active.map((job) =>
      fetchWithAuth(buildUrl(`/jobs/${job.jobId}/cancel`), {
        method: "POST",
      }).catch((error) => {
        console.error(error);
        return null;
      }),
    ),
  );
}

async function cancelFnvJobs(name, jobs) {
  const cancelButton = document.getElementById(`${name}CancelButton`);
  cancelButton.disabled = true;
  // отмена подтверждается строками списка, а не отдельным сообщением:
  // итог по всей группе придёт один - в renderFnvSummary
  jobs
    .filter((job) => !isFnvTerminal(job))
    .forEach((job) => {
      job.stopping = true;
      fnvRenderState(job);
    });
  await fnvSendCancel(jobs);
  cancelButton.classList.add("d-none");
}

async function fnvWatchJob(name, job, jobs) {
  try {
    const data = await waitJobTerminal(job.jobId);
    const status = data && data.job ? data.job.status : null;
    if (status === "completed") {
      job.state = "completed";
    } else if (status === "cancelled") {
      job.state = "cancelled";
    } else {
      // текст ошибки смотрим только в консоли и в fnv.log архива
      console.error(`Job ${job.jobId} failed:`, data && data.job);
      job.state = "error";
    }
  } catch (error) {
    console.error(error);
    job.state = "error";
  }
  job.stopping = false;
  fnvRenderState(job);
  updateFnvProgress(name, jobs);
  if (job.state === "error") {
    job.hasArchive = await fnvArchiveExists(job);
    fnvRenderState(job);
  }
}

function renderFnvSummary(name, jobs) {
  renderFnvBundle(name, jobs);
  const failed = jobs.filter((job) => job.state === "error");
  const cancelled = jobs.filter((job) => job.state === "cancelled");
  if (failed.length) {
    showFormAlert(
      name,
      `Ошибка при обработке ${failed.length} из ${jobs.length} ` +
        "месторождений — логи можно скачать в списке выше",
    );
  } else if (cancelled.length) {
    showFormWarning(name, `Отменено: ${cancelled.length} из ${jobs.length}`);
  } else {
    document.getElementById(`${name}Success`).classList.remove("d-none");
  }
}

function renderFnvBundle(name, jobs) {
  const link = document.getElementById(`${name}Bundle`);
  link.classList.add("d-none");
  // в сборку идут только полностью посчитанные поля и те, где остался
  // архив с логом. Отменённые исключаем осознанно: серверный архив у них
  // бывает частичным, и огрызок в общем архиве путает сильнее, чем его
  // отсутствие - такой файл остаётся доступен в «Истории отчетов»
  const archived = jobs.filter(
    (job) => job.state === "completed" || job.state === "error",
  );
  if (!archived.length) {
    return;
  }
  link.onclick = (event) => {
    event.preventDefault();
    buildFnvArchive(name, link, archived);
  };
  link.classList.remove("d-none");
}

/* Собрать один архив из результатов всех месторождений.
 *
 * Каждое месторождение - отдельный zip, который отдаёт сервер. Скачиваем их
 * по очереди, распаковываем в память (JSZip) и складываем содержимое в один
 * архив с папкой месторождения на верхнем уровне. Бэкенд при этом не
 * меняется - файлы уже лежат на диске по одному архиву на задачу.
 */
async function buildFnvArchive(name, link, archived) {
  const label = link.querySelector(".fnv-bundle-label");
  const zip = new JSZip();
  const failed = [];
  link.classList.add("disabled");
  try {
    for (const [index, job] of archived.entries()) {
      label.textContent = `Скачивание ${index + 1} из ${archived.length}…`;
      try {
        await addFnvField(zip, job);
      } catch (error) {
        console.error(`Не удалось добавить ${job.field.name}`, error);
        failed.push(job.field.name);
      }
    }
    label.textContent = "Упаковка архива…";
    const blob = await zip.generateAsync({
      type: "blob",
      compression: "DEFLATE",
    });
    saveBlob(blob, fnvArchiveName());
    if (failed.length) {
      showFormWarning(
        name,
        `В архив вошли не все месторождения: ${failed.join(", ")}`,
      );
    }
  } catch (error) {
    console.error(error);
    showDefaultFormAlert(name);
  } finally {
    link.classList.remove("disabled");
    label.textContent = "Скачать все результаты";
  }
}

function fnvArchiveName() {
  // двоеточие в имени файла Windows не допускает - заменяем на дефис
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  return `fnv_${stamp}.zip`;
}

async function addFnvField(zip, job) {
  const response = await fetchWithAuth(
    buildUrl(`/reports/${job.fileId}/zip`),
  );
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  const archive = await JSZip.loadAsync(await response.arrayBuffer());
  // сервер отдаёт архив с папкой месторождения на верхнем уровне,
  // в общем архиве своя папка задаёт имя - лишний уровень убираем
  const folder = zip.folder(job.field.name);
  for (const [entry, item] of Object.entries(archive.files)) {
    if (item.dir) {
      continue;
    }
    const parts = entry.split("/");
    // снимаем верхний уровень только если он действительно папка поля
    const known = parts.length > 1 && parts[0] === job.field.name;
    folder.file(
      (known ? parts.slice(1) : parts).join("/"),
      await item.async("uint8array"),
    );
  }
}

function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function loadFNV(name) {
  if (fnvRunning) {
    return;
  }
  const loader = document.getElementById(`${name}Status`);
  const button = document.getElementById(`${name}Button`);
  const cancelButton = document.getElementById(`${name}CancelButton`);
  const minRadius = document.getElementById(`${name}MinRadius`).value;
  const alternative = document.getElementById(`${name}Alternative`).checked;
  const fields = collectFnvFields(name);

  // остальные проверки формы делает assignWork сам, но до первой
  // итерации цикла управление не дойдёт - пустой выбор проверяем тут
  if (!fields.length) {
    validateForm(name);
    showFormAlert(name, "Выберите месторождения");
    return;
  }

  fnvRunning = true;
  hideStatusAlerts(name);
  document.getElementById(`${name}Progress`).classList.remove("d-none");
  document.getElementById(`${name}FieldList`).replaceChildren();
  document.getElementById(`${name}Bundle`).classList.add("d-none");
  updateFnvProgress(name, []);
  loader.classList.remove("d-none");
  button.classList.add("disabled");
  cancelButton.classList.remove("d-none");
  cancelButton.disabled = false;

  const jobs = [];
  cancelButton.onclick = async () => {
    fnvCancelRequested = true;
    await cancelFnvJobs(name, jobs);
  };

  try {
    for (const field of fields) {
      const result = await assignWork(name, `/reports/${name}`, {
        field: field,
        min_radius: minRadius,
        alternative: alternative,
      });
      if (!result) {
        // задача не создана - уже созданные останавливаем, а панель
        // прогресса прячем: ничего изначально не запускалось
        await fnvSendCancel(jobs);
        document.getElementById(`${name}Progress`).classList.add("d-none");
        return;
      }
      const job = fnvAddFieldRow(name, {
        field: field,
        jobId: result.job.job_id,
        fileId: result.job.file_id,
        state: "queued",
      });
      jobs.push(job);
      fnvRenderState(job);
      updateFnvProgress(name, jobs);
      if (fnvCancelRequested) {
        // отмена нажата, пока очередь задач ещё создавалась
        await fnvSendCancel([job]);
      }
    }
    await Promise.all(jobs.map((job) => fnvWatchJob(name, job, jobs)));
    renderFnvSummary(name, jobs);
  } catch (error) {
    console.error(error);
    showDefaultFormAlert(name);
  } finally {
    loader.classList.add("d-none");
    button.classList.remove("disabled");
    cancelButton.classList.add("d-none");
    fnvRunning = false;
    fnvCancelRequested = false;
  }
}
