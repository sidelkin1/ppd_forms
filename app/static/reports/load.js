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

  const url = `/report/${reportName}`;
  const data = {
    date_from: dateFrom,
    date_to: dateTo,
  };
  const result = await assignWork(reportName, url, data);
  if (result) {
    checkStatus(reportName, result.job.job_id);
  }

  link.href = `/report/${result.job.file_id}`;
  loader.classList.add("d-none");
  button.classList.remove("disabled");
}
