async function fetchJobStatus(jobID) {
  const response = await fetchWithAuth(buildUrl(`/jobs/${jobID}`));
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return await response.json();
}

async function waitJobTerminal(jobID) {
  const webSocketClient = new WebSocketClient();
  try {
    await webSocketClient.connect(buildUrl(`/jobs/${jobID}/ws`));
    return JSON.parse(await webSocketClient.receive());
  } finally {
    await webSocketClient.disconnect();
  }
}

function showCancelButton(name, jobID) {
  const button = document.getElementById(`${name}CancelButton`);
  if (!button) {
    return;
  }
  button.classList.remove("d-none");
  button.disabled = false;
  button.onclick = () => cancelJob(name, jobID);
}

function hideCancelButton(name) {
  document.getElementById(`${name}CancelButton`)?.classList.add("d-none");
}

function renderJobResponse(name, data, resultURL) {
  hideStatusAlerts(name);
  if (data.job.status === "completed") {
    document.getElementById(`${name}Success`).classList.remove("d-none");
    const link = document.getElementById(`${name}Link`);
    if (resultURL && link) {
      link.href = buildUrl(resultURL);
    }
    return true;
  }
  if (data.job.status === "cancelled") {
    showFormWarning(name);
  } else if (data.job.message) {
    showFormAlert(name, data.job.message);
  } else {
    showDefaultFormAlert(name);
  }
  return false;
}

async function checkStatus(name, jobID, resultURL = null) {
  hideStatusAlerts(name);
  showCancelButton(name, jobID);
  try {
    const data = await waitJobTerminal(jobID);
    return renderJobResponse(name, data, resultURL);
  } catch (error) {
    console.error(error);
    showDefaultFormAlert(name);
    return false;
  } finally {
    hideCancelButton(name);
  }
}

async function cancelJob(name, jobID) {
  const btn = document.getElementById(`${name}CancelButton`);
  btn.disabled = true;
  try {
    const response = await fetchWithAuth(buildUrl(`/jobs/${jobID}/cancel`), {
      method: "POST",
    });
    switch (response.status) {
      case 202:
        showFormWarning(name, "Отмена запрошена…");
        btn.classList.add("d-none");
        break;
      case 404:
        showFormAlert(name, "Задача не найдена");
        btn.classList.add("d-none");
        break;
      case 200:
      case 409:
        btn.classList.add("d-none");
        break;
      default:
        showDefaultFormAlert(name);
        btn.disabled = false;
    }
  } catch (error) {
    console.error(error);
    showDefaultFormAlert(name);
    btn.disabled = false;
  }
}
