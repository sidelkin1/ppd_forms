// custom javascript

(function () {
  console.log("Sanity Check!");
})();

var rowCounter = -1;

function handleClick(date_from, date_to) {
  fetch("/report", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ date_from: date_from, date_to: date_to }),
  })
    .then((response) => response.json())
    .then((data) => {
      rowCounter = rowCounter + 1;
      getStatus(data.file_id, rowCounter);
    });
}

function getStatus(file_id, rowCounter) {
  fetch(`/report/${file_id}/status`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) =>
      response.json().then((data) => ({
        data: data,
        status: response.status,
      }))
    )
    .then((res) => {
      console.log(res.data);

      let result
      if (res.status === 200) {
        result = `<a href="/report/${file_id}">Ссылка на файл</a>`;
      }
      else {
        result = "..."
      }

      const html = `
        <tr>
          <td>${file_id}</td>
          <td>${res.data.message}</td>
          <td>${result}</td>
        </tr>`;
      const tasks = document.getElementById("tasks");
      if (rowCounter < tasks.rows.length) {
        tasks.deleteRow(rowCounter);
      }
      const newRow = tasks.insertRow(rowCounter);
      newRow.innerHTML = html;
      
      if (res.status === 200) {
        rowCounter = rowCounter - 1;
        return false;
      }        
      
      setTimeout(function () {
        getStatus(file_id, rowCounter);
      }, 1000);
    })
    .catch((err) => console.log(err));
}
