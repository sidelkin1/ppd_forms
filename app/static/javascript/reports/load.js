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
    link.href = `/reports/${result.job.file_id}`;
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
    link.href = `/reports/${result.job.file_id}`;
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
    link.href = `/reports/${result.job.file_id}`;
    await checkStatus(reportName, result.job.job_id);
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}
