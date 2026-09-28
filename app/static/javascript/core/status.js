async function checkStatus(name, jobID, resultURL = null) {
  const cancelButton = document.getElementById(`${name}CancelButton`);

  let result = false;
  const webSocketClient = new WebSocketClient();
  hideStatusAlerts(name);
  try {
    const url = buildUrl(`/jobs/${jobID}/ws`);
    await webSocketClient.connect(url);
    while (true) {
      const response = await webSocketClient.receive();
      const data = JSON.parse(response);
      if (data.job.status === "in_progress") {
        if (cancelButton) {
          cancelButton.classList.remove("d-none");
          cancelButton.disabled = false;
          cancelButton.onclick = () => cancelJob(name, jobID);
        }
        continue;
      }
      hideStatusAlerts(name);
      if (data.job.status === "completed") {
        document.getElementById(`${name}Success`).classList.remove("d-none");
        const link = document.getElementById(`${name}Link`);
        if (resultURL && link) {
          link.href = buildUrl(resultURL);
        }
        result = true;
      } else if (data.job.status === "cancelled") {
        showFormWarning(name);
      } else if (data.job.message) {
        showFormAlert(name, data.job.message);
      } else {
        showDefaultFormAlert(name);
      }
      break;
    }
  } catch (error) {
    console.error(error);
    showDefaultFormAlert(name);
  } finally {
    cancelButton?.classList.add("d-none");
    await webSocketClient.disconnect();
  }

  return result;
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
