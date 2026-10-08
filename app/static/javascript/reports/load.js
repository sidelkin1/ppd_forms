async function sendReportFiles(name, files, url) {
  resetFormAlert(name);
  clearFormErrors(name);
  if (!validateForm(name)) {
    showFormAlert(name, "Заполните обязательные поля");
    return;
  }

  try {
    const results = await sendMultipleFiles(files, url);
    return results;
  } catch (error) {
    console.error(error);
    showDefaultFormAlert(name);
  }
}

async function loadReport(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const dateFrom = document.getElementById(`${reportName}Start`).value;
  const dateTo = document.getElementById(`${reportName}End`).value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const url = `/reports/${reportName}`;
  const data = {
    date_from: dateFrom,
    date_to: dateTo,
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

async function loadOnDate(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const onDate = document.getElementById(`${reportName}OnDate`).value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const url = `/reports/${reportName}`;
  const data = { on_date: onDate };
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

async function loadInjLoss(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const dateFrom = document.getElementById(`${reportName}Start`).value;
  const dateTo = document.getElementById(`${reportName}End`).value;
  const lossMode = document.getElementById(`${reportName}Select`).value;
  const neighbs = document.getElementById(`${reportName}Neighbs`).checked;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const url = `/reports/${reportName}/${lossMode}`;
  const data = {
    date_from: dateFrom,
    date_to: dateTo,
    neighbs_from_ns_ppd: neighbs,
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

async function loadOilLoss(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const dateFrom = document.getElementById(`${reportName}Start`).value;
  const dateTo = document.getElementById(`${reportName}End`).value;
  const lossMode = document.getElementById(`${reportName}Select`).value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const url = `/reports/${reportName}/${lossMode}`;
  const data = {
    date_from: dateFrom,
    date_to: dateTo,
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

async function loadMatrix(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const dateFrom = document.getElementById(`${reportName}Start`).value;
  const dateTo = document.getElementById(`${reportName}End`).value;
  const basePeriod = document.getElementById(`${reportName}Base`).value;
  const predPeriod = document.getElementById(`${reportName}Pred`).value;
  const onDate = document.getElementById(`${reportName}Mer`).value;
  const excludes = [
    ...document.getElementById(`${reportName}Excludes`).selectedOptions,
  ]
    .filter((opt) => opt.value !== "--")
    .map((opt) => opt.value);
  const wells = document.getElementById(`${reportName}Wells`).files[0];

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const files = await sendReportFiles(reportName, [wells], "/excel/");
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      date_from: dateFrom,
      date_to: dateTo,
      excludes: excludes,
      base_period: basePeriod,
      pred_period: predPeriod || null,
      on_date: onDate || null,
      wells: files[0]?.filename || null,
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

async function loadMatbal(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const { value: fieldID, text: fieldName } = document.getElementById(
    `${reportName}Fields`,
  ).selectedOptions[0];
  const reservoirs = [
    ...document.getElementById(`${reportName}Reservoirs`).selectedOptions,
  ]
    .filter((opt) => opt.value !== "--")
    .map((opt) => ({ id: opt.value, name: opt.text }));
  const wells = document
    .getElementById(`${reportName}Wells`)
    .value.split(/[,;\s]+/)
    .filter((well) => well);
  const alternative = document.getElementById(
    `${reportName}Alternative`,
  ).checked;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const url = `/reports/${reportName}`;
  const data = {
    field: { id: fieldID, name: fieldName },
    reservoirs: reservoirs,
    wells: wells,
    alternative: alternative,
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

async function loadProlong(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const expected = document.getElementById(`${reportName}Expected`).files[0];
  const actual = document.getElementById(`${reportName}Actual`).files[0];
  const allMethods = [...document.getElementById(`${reportName}Interpolation`)]
    .filter((opt) => opt.value !== "all")
    .map((opt) => opt.value);
  const interpolation = document.getElementById(`${reportName}Interpolation`)
    .selectedOptions[0].value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const files = await sendReportFiles(
    reportName,
    [expected, actual],
    "/excel/",
  );
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      expected: files[0]?.filename || null,
      actual: files[1]?.filename || null,
      interpolations: interpolation === "all" ? allMethods : [interpolation],
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

async function loadMMB(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const tanks = document.getElementById(`${reportName}Tank`).files[0];
  const alternative = document.getElementById(
    `${reportName}Alternative`,
  ).checked;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const files = await sendReportFiles(reportName, [tanks], "/excel/");
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      file: files[0]?.filename || null,
      alternative: alternative,
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

async function loadWellTest(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const wellTest = document.getElementById(`${reportName}WellTest`).files[0];
  const gtmPeriod = document.getElementById(`${reportName}GtmPeriod`).value;
  const gdisPeriod = document.getElementById(`${reportName}GdisPeriod`).value;
  const radius = document.getElementById(`${reportName}Radius`).value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const files = await sendReportFiles(reportName, [wellTest], "/excel/");
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      file: files[0]?.filename || null,
      gtm_period: gtmPeriod,
      gdis_period: gdisPeriod,
      radius: radius,
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

async function loadOwcResp(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const { value: fieldID, text: fieldName } = document.getElementById(
    `${reportName}Fields`,
  ).selectedOptions[0];
  const { value: reservoirID, text: reservoirName } = document.getElementById(
    `${reportName}Reservoirs`,
  ).selectedOptions[0];
  const well = document.getElementById(`${reportName}Well`).value;
  const pressure = document.getElementById(`${reportName}Pressure`).value;
  const depth = document.getElementById(`${reportName}Depth`).value;
  const wellTest = document.getElementById(`${reportName}WellTest`).value;
  const onDate = document.getElementById(`${reportName}OnDate`).value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  hideStatusAlerts(reportName);

  const url = `/reports/${reportName}`;
  const data = {
    field: { id: fieldID, name: fieldName },
    reservoir: { id: reservoirID, name: reservoirName },
    well: well,
    pressure: pressure,
    depth: depth,
    well_test: wellTest,
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
