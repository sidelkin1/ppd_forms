function constructWebSocketURL(relaivePath) {
  const url = new URL(location.href);
  url.protocol = "ws";
  url.pathname = relaivePath;
  return url;
}

async function checkStatus(name, jobID, resultURL = null) {
  const success = document.getElementById(`${name}Success`);
  const alert = document.getElementById(`${name}Danger`);
  const link = document.getElementById(`${name}Link`);

  let result;
  const webSocketClient = new WebSocketClient();
  try {
    const url = constructWebSocketURL(buildUrl(`/jobs/${jobID}/ws`));
    await webSocketClient.connect(url);
    const response = await webSocketClient.receive();
    const data = JSON.parse(response);
    if (data.job.status !== "completed") {
      throw new Error(data.job.message);
    }
    success.classList.remove("d-none");
    if (resultURL) {
      link.href = buildUrl(resultURL);
    }
    result = true;
  } catch (error) {
    console.error(error);
    alert.classList.remove("d-none");
    result = false;
  } finally {
    await webSocketClient.disconnect();
  }

  return result;
}
