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
