// custom javascript

(function () {
  console.log("Sanity Check!");
})();

let rowCounter = 0;
const results = new Map();

function handleClick(date_from, date_to) {
  fetch("/report/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      date_from: date_from,
      date_to: date_to
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      const html = `
        <tr>
          <td>${data.file_id}</td>
          <td>Отчет не готов!</td>
          <td>...</td>
        </tr>`;
      const tasks = document.getElementById("tasks");
      const newRow = tasks.insertRow(rowCounter);
      newRow.innerHTML = html;
      results.set(data.file_id, rowCounter++);
    });
}

const ws = new WebSocket("ws://127.0.0.1:8000/report/ws");
ws.onmessage = function (event) {
  console.log(JSON.parse(event.data));
  // const file_id = event.data;
  // const row = results.get(file_id);
  // const html = `
  //   <tr>
  //     <td>${file_id}</td>
  //     <td>Отчет готов!</td>
  //     <td><a href="/report/${file_id}">Ссылка на файл</a></td>
  //   </tr>`;
  // const tasks = document.getElementById("tasks");
  // tasks.deleteRow(row);
  // const newRow = tasks.insertRow(row);
  // newRow.innerHTML = html;
};

function sendMessage(date_from, date_to) {
  const json = JSON.stringify({
    task_id: "report",
    name: "profile",
    date_from: date_from,
    date_to: date_to
  });
  ws.send(json);
}

function sendMessage2(date_from, date_to) {
  const json = JSON.stringify({
    task_id: "database",
    table: "report",
    mode: "refresh",
    date_from: date_from,
    date_to: date_to
  });
  ws.send(json);
}

// function getStatus(file_id, rowCounter) {
//   fetch(`/report/${file_id}/status`, {
//     method: "GET",
//     headers: {
//       "Content-Type": "application/json",
//     },
//   })
//     .then((response) =>
//       response.json().then((data) => ({
//         data: data,
//         status: response.status,
//       }))
//     )
//     .then((res) => {
//       console.log(res.data);

//       let result;
//       if (res.status === 200) {
//         result = `<a href="/report/${file_id}">Ссылка на файл</a>`;
//       } else {
//         result = "...";
//       }

//       const html = `
//         <tr>
//           <td>${file_id}</td>
//           <td>${res.data.message}</td>
//           <td>${result}</td>
//         </tr>`;
//       const tasks = document.getElementById("tasks");
//       if (rowCounter < tasks.rows.length) {
//         tasks.deleteRow(rowCounter);
//       }
//       const newRow = tasks.insertRow(rowCounter);
//       newRow.innerHTML = html;

//       if (res.status === 200) {
//         rowCounter = rowCounter - 1;
//         return false;
//       }

//       setTimeout(function () {
//         getStatus(file_id, rowCounter);
//       }, 1000);
//     })
//     .catch((err) => console.log(err));
// }

// async function showCookies() {
//   let response = await fetch("/cookie/", { method: "POST" });
//   let json = await response.json();
//   alert(json.message);
//   const output = document.getElementById("cookies");
//   output.textContent = `> ${document.cookie}`;
// }

// function clearOutputCookies() {
//   const output = document.getElementById("cookies");
//   output.textContent = "";
// }

// var ws = new WebSocket("ws://localhost:8000/ws");
// var ws2 = new WebSocket("ws://localhost:8000/ws");
// ws.onmessage = function (event) {
//   var messages = document.getElementById("messages");
//   var message = document.createElement("li");
//   var content = document.createTextNode(event.data);
//   message.appendChild(content);
//   messages.appendChild(message);
// };
// function sendMessage(event) {
//   var input = document.getElementById("messageText");
//   ws.send(input.value);
//   input.value = "";
//   event.preventDefault();
// }
