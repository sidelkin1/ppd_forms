(() => {
  console.log("Sanity Check!");
})();

var tooltipTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
);
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl, {
    container: "body",
    trigger: "hover",
  });
});

function copyClipboard(id, text) {
  navigator.clipboard.writeText(text);
  let tooltip = bootstrap.Tooltip.getInstance(`#${id}`);
  const oldTitle = tooltip._config.title;
  tooltip._config.title = text;
  tooltip.update();
  tooltip.show();
  tooltip._config.title = oldTitle;
}

function buildUrl(endpoint) {
  return `${ROOT_PATH}${endpoint}`;
}

let requestIds = {};

function setRequestId(uniqueKey) {
  if (!requestIds[uniqueKey]) {
    requestIds[uniqueKey] = 1;
  }
  return ++requestIds[uniqueKey];
}

function getRequestId(uniqueKey) {
  return requestIds[uniqueKey];
}

async function fetchWithAuth(url, options = {}) {
  const response = await fetch(url, options);
  if (response.status === 401) {
    window.location.href = `${LOGIN_URL}?next=${encodeURIComponent(
      window.location.pathname + window.location.search
    )}`;
  }
  return response;
}
