document.addEventListener("DOMContentLoaded", () => {
  fetchJobs();
});

async function fetchJobs() {
  try {
    const response = await fetch(buildUrl("/jobs/scheduled?task_id=report"));
    const data = await response.json();
    const tableBody = document.getElementById("jobsTableBody");
    tableBody.innerHTML = "";
    data.sort(
      (a, b) => new Date(b.job.created_at) - new Date(a.job.created_at)
    );
    data.forEach((response) => {
      const row = createJobRow(response);
      tableBody.appendChild(row);
      updateJobStatus(response.job.job_id);
    });
  } catch (error) {
    console.error("Error:", error);
  }
}

function createJobRow(response) {
  const row = document.createElement("tr");
  row.innerHTML = `
        <td>${response.task.name}</td>
        <td>${new Date(response.job.created_at).toLocaleString()}</td>
        <td id="status-${response.job.job_id}">
            <div class="spinner-border spinner-border-sm" role="status"></div>
        </td>
        <td id="action-${response.job.job_id}"></td>
    `;
  return row;
}

async function updateJobStatus(jobId) {
  try {
    const response = await fetch(buildUrl(`/jobs/${jobId}`));
    const data = await response.json();
    updateJobStatusUI(jobId, data);
  } catch (error) {
    console.error("Error:", error);
  }
}

function updateJobStatusUI(jobId, data) {
  const statusCell = document.getElementById(`status-${jobId}`);
  const actionCell = document.getElementById(`action-${jobId}`);
  statusCell.textContent = data.job.status;

  switch (data.job.status) {
    case "completed":
      actionCell.innerHTML = `<a href="${buildUrl(
        `/reports/${data.job.file_id}/zip`
      )}" class="btn btn-success btn-sm">Скачать</a>`;
      break;
    case "error":
      actionCell.textContent = data.job.message || "Произошла ошибка";
      break;
    case "not_found":
      actionCell.textContent = "N/A";
      break;
    case "in_progress":
      actionCell.innerHTML = `
                <button class="btn btn-primary btn-sm" onclick="getResult('${jobId}')">
                Получить
                </button>
            `;
      break;
  }
}

async function getResult(jobId) {
  const actionCell = document.getElementById(`action-${jobId}`);
  actionCell.innerHTML = `
        <div class="spinner-border spinner-border-sm" role="status"></div>
    `;

  const webSocketClient = new WebSocketClient();
  const url = buildUrl(`/jobs/${jobId}/ws`);

  try {
    await webSocketClient.connect(url);
    const response = await webSocketClient.receive();
    const data = JSON.parse(response);
    updateJobStatusUI(jobId, data);
  } catch (error) {
    console.error("Error:", error);
    updateJobStatusUI(jobId, {
      status: "error",
      message: "Ошибка соединения",
    });
  } finally {
    await webSocketClient.disconnect();
  }
}
