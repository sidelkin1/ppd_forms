async function sendReportFiles(name, files, url) {
  const alert = document.getElementById(`${name}Danger`);

  try {
    results = await sendMultipleFiles(files, url);
    return results;
  } catch (error) {
    console.error(error);
    alert.classList.remove("d-none");
  }
}

async function loadReport(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const dateFrom = document.getElementById(`${reportName}Start`).value;
  const dateTo = document.getElementById(`${reportName}End`).value;
  const link = document.getElementById(`${reportName}Link`);

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const url = `/reports/${reportName}`;
  const data = {
    date_from: dateFrom,
    date_to: dateTo,
  };
  const result = await assignWork(reportName, url, data);
  if (result) {
    link.href = `/reports/${result.job.file_id}/csv`;
    await checkStatus(reportName, result.job.job_id);
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function loadInjLoss(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const dateFrom = document.getElementById(`${reportName}Start`).value;
  const dateTo = document.getElementById(`${reportName}End`).value;
  const lossMode = document.getElementById(`${reportName}Select`).value;
  const link = document.getElementById(`${reportName}Link`);

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const url = `/reports/${reportName}/${lossMode}`;
  const data = {
    date_from: dateFrom,
    date_to: dateTo,
  };
  const result = await assignWork(reportName, url, data);
  if (result) {
    link.href = `/reports/${result.job.file_id}/csv`;
    await checkStatus(reportName, result.job.job_id);
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function loadMatrix(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const dateFrom = document.getElementById(`${reportName}Start`).value;
  const dateTo = document.getElementById(`${reportName}End`).value;
  const basePeriod = document.getElementById(`${reportName}Base`).value;
  const predPeriod = document.getElementById(`${reportName}Pred`).value;
  const onDate = document.getElementById(`${reportName}Mer`).value;
  const link = document.getElementById(`${reportName}Link`);
  const excludes = [
    ...document.getElementById(`${reportName}Excludes`).selectedOptions,
  ]
    .filter((opt) => opt.value !== "--")
    .map((opt) => opt.value);

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const url = `/reports/${reportName}`;
  const data = {
    date_from: dateFrom,
    date_to: dateTo,
    excludes: excludes,
    base_period: basePeriod,
    pred_period: predPeriod,
    on_date: onDate,
  };
  const result = await assignWork(reportName, url, data);
  if (result) {
    link.href = `/reports/${result.job.file_id}/csv`;
    await checkStatus(reportName, result.job.job_id);
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function loadFNV(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const minRadius = document.getElementById(`${reportName}MinRadius`).value;
  const allFields = [...document.getElementById(`${reportName}Fields`)]
    .filter((opt) => !["--", "0"].includes(opt.value))
    .map((opt) => ({ id: opt.value, name: opt.text }));
  const { value: fieldID, text: fieldName } = document.getElementById(
    `${reportName}Fields`
  ).selectedOptions[0];
  const alternative = document.getElementById(
    `${reportName}Alternative`
  ).checked;
  const link = document.getElementById(`${reportName}Link`);

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const url = `/reports/${reportName}`;
  const data = {
    fields: fieldID === "0" ? allFields : [{ id: fieldID, name: fieldName }],
    min_radius: minRadius,
    alternative: alternative,
  };
  const result = await assignWork(reportName, url, data);
  if (result) {
    link.href = `/reports/${result.job.file_id}/zip`;
    await checkStatus(reportName, result.job.job_id);
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function loadMatbal(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const { value: fieldID, text: fieldName } = document.getElementById(
    `${reportName}Fields`
  ).selectedOptions[0];
  const reservoirs = [
    ...document.getElementById(`${reportName}Reservoirs`).selectedOptions,
  ]
    .filter((opt) => opt.value !== "--")
    .map((opt) => ({ id: opt.value, name: opt.text }));
  const wells = document.getElementById(`${reportName}Wells`).files[0];
  const measurements = document.getElementById(`${reportName}Measurements`)
    .files[0];
  const alternative = document.getElementById(
    `${reportName}Alternative`
  ).checked;
  const link = document.getElementById(`${reportName}Link`);

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const files = await sendReportFiles(
    reportName,
    [wells, measurements],
    "/excel"
  );
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      field: { id: fieldID, name: fieldName },
      reservoirs: reservoirs,
      wells: files[0] ? files[0].filename : null,
      measurements: files[1] ? files[1].filename : null,
      alternative: alternative,
    };
    const result = await assignWork(reportName, url, data);
    if (result) {
      link.href = `/reports/${result.job.file_id}/zip`;
      await checkStatus(reportName, result.job.job_id);
    }
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function loadProlong(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const expected = document.getElementById(`${reportName}Expected`).files[0];
  const actual = document.getElementById(`${reportName}Actual`).files[0];
  const interpolation = document.getElementById(`${reportName}Interpolation`)
    .selectedOptions[0].value;
  const link = document.getElementById(`${reportName}Link`);

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const files = await sendReportFiles(reportName, [expected, actual], "/excel");
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      expected: files[0] ? files[0].filename : null,
      actual: files[1] ? files[1].filename : null,
      interpolation: interpolation,
    };
    const result = await assignWork(reportName, url, data);
    if (result) {
      link.href = `/reports/${result.job.file_id}/zip`;
      await checkStatus(reportName, result.job.job_id);
    }
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}
