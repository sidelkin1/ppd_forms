function checkStatus(name, jobID) {
  const success = document.getElementById(`${name}Success`);
  const alert = document.getElementById(`${name}Danger`);

  const socket = new WebSocket(`ws://127.0.0.1:8000/job/${jobID}/ws`);

  socket.onopen = () => {
    console.log("WebSocket connection opened");
  };

  socket.onclose = () => {
    console.log("WebSocket connection closed");
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
    alert.classList.remove("d-none");
  };

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.job.status !== "completed") {
      console.error(data.job.message);
      alert.classList.remove("d-none");
      return;
    }
    success.classList.remove("d-none");
  };
}
