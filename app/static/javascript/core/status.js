async function checkStatus(name, jobID, resultURL = null) {
  const success = document.getElementById(`${name}Success`);
  const link = document.getElementById(`${name}Link`);

  let result;
  let jobMessage = null;
  const webSocketClient = new WebSocketClient();
  try {
    const url = buildUrl(`/jobs/${jobID}/ws`);
    await webSocketClient.connect(url);
    const response = await webSocketClient.receive();
    const data = JSON.parse(response);
    if (data.job.status !== "completed") {
      jobMessage = data.job.message;
      throw new Error(jobMessage);
    }
    success.classList.remove("d-none");
    if (resultURL) {
      link.href = buildUrl(resultURL);
    }
    result = true;
  } catch (error) {
    console.error(error);
    if (jobMessage) {
      showFormAlert(name, jobMessage);
    } else {
      showDefaultFormAlert(name);
    }
    result = false;
  } finally {
    await webSocketClient.disconnect();
  }

  return result;
}
