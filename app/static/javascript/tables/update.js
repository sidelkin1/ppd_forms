async function updateTable(tableName) {
  const loader = document.getElementById(`${tableName}Status`);
  const button = document.getElementById(`${tableName}Button`);
  const alert = document.getElementById(`${tableName}Danger`);
  const success = document.getElementById(`${tableName}Success`);
  const dateFrom = document.getElementById(`${tableName}Start`).value;
  const dateTo = document.getElementById(`${tableName}End`).value;

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  const url = `/database/${tableName}/refresh`;
  const data = {
    date_from: dateFrom,
    date_to: dateTo,
  };
  const result = await assignWork(tableName, url, data);
  if (result) {
    await checkStatus(tableName, result.job.job_id);
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}

async function updateExcel(tableName) {
  const loader = document.getElementById(`${tableName}Status`);
  const button = document.getElementById(`${tableName}Button`);
  const alert = document.getElementById(`${tableName}Danger`);
  const success = document.getElementById(`${tableName}Success`);

  loader.classList.remove("d-none");
  button.classList.add("disabled");
  alert.classList.add("d-none");
  success.classList.add("d-none");

  let result = await sendFile(tableName, "/excel/");
  if (result) {
    const url = `/excel/${tableName}/refresh`;
    const data = { file: result.filename };
    result = await assignWork(tableName, url, data);
  }
  if (result) {
    await checkStatus(tableName, result.job.job_id);
  }

  loader.classList.add("d-none");
  button.classList.remove("disabled");
}
