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
    await checkStatus(
      reportName,
      result.job.job_id,
      `/reports/${result.job.file_id}/zip`
    );
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function loadOnDate(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const onDate = document.getElementById(`${reportName}OnDate`).value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const url = `/reports/${reportName}`;
  const data = { on_date: onDate };
  const result = await assignWork(reportName, url, data);
  if (result) {
    await checkStatus(
      reportName,
      result.job.job_id,
      `/reports/${result.job.file_id}/zip`
    );
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
    await checkStatus(
      reportName,
      result.job.job_id,
      `/reports/${result.job.file_id}/zip`
    );
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
  const excludes = [
    ...document.getElementById(`${reportName}Excludes`).selectedOptions,
  ]
    .filter((opt) => opt.value !== "--")
    .map((opt) => opt.value);
  const wells = document.getElementById(`${reportName}Wells`).files[0];

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const files = await sendReportFiles(reportName, [wells], "/excel/");
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      date_from: dateFrom,
      date_to: dateTo,
      excludes: excludes,
      base_period: basePeriod,
      pred_period: predPeriod,
      on_date: onDate,
      wells: files[0] ? files[0].filename : null,
    };
    const result = await assignWork(reportName, url, data);
    if (result) {
      await checkStatus(
        reportName,
        result.job.job_id,
        `/reports/${result.job.file_id}/zip`
      );
    }
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
    await checkStatus(
      reportName,
      result.job.job_id,
      `/reports/${result.job.file_id}/zip`
    );
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

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const files = await sendReportFiles(
    reportName,
    [wells, measurements],
    "/excel/"
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
      await checkStatus(
        reportName,
        result.job.job_id,
        `/reports/${result.job.file_id}/zip`
      );
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

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const files = await sendReportFiles(
    reportName,
    [expected, actual],
    "/excel/"
  );
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      expected: files[0] ? files[0].filename : null,
      actual: files[1] ? files[1].filename : null,
      interpolation: interpolation,
    };
    const result = await assignWork(reportName, url, data);
    if (result) {
      await checkStatus(
        reportName,
        result.job.job_id,
        `/reports/${result.job.file_id}/zip`
      );
    }
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function loadMMB(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const tanks = document.getElementById(`${reportName}Tank`).files[0];
  const alternative = document.getElementById(
    `${reportName}Alternative`
  ).checked;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const files = await sendReportFiles(reportName, [tanks], "/excel/");
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      file: files[0] ? files[0].filename : null,
      alternative: alternative,
    };
    const result = await assignWork(reportName, url, data);
    if (result) {
      await checkStatus(
        reportName,
        result.job.job_id,
        `/reports/${result.job.file_id}/zip`
      );
    }
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function loadWellTest(reportName) {
  const loader = document.getElementById(`${reportName}Status`);
  const button = document.getElementById(`${reportName}Button`);
  const alert = document.getElementById(`${reportName}Danger`);
  const success = document.getElementById(`${reportName}Success`);
  const wellTest = document.getElementById(`${reportName}WellTest`).files[0];
  const gtmPeriod = document.getElementById(`${reportName}GtmPeriod`).value;
  const gdisPeriod = document.getElementById(`${reportName}GdisPeriod`).value;
  const radius = document.getElementById(`${reportName}Radius`).value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const files = await sendReportFiles(reportName, [wellTest], "/excel/");
  if (files) {
    const url = `/reports/${reportName}`;
    const data = {
      file: files[0] ? files[0].filename : null,
      gtm_period: gtmPeriod,
      gdis_period: gdisPeriod,
      radius: radius,
    };
    const result = await assignWork(reportName, url, data);
    if (result) {
      await checkStatus(
        reportName,
        result.job.job_id,
        `/reports/${result.job.file_id}/zip`
      );
    }
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}
