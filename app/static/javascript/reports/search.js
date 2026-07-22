document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("reportSearch");
  const reportCards = document.querySelectorAll(".report-card");
  const reportCount = document.getElementById("reportCount");

  if (!searchInput) return;

  searchInput.addEventListener("input", function () {
    const query = this.value.toLowerCase().trim();
    let visibleCount = 0;

    reportCards.forEach(function (card) {
      const searchData = (card.dataset.search || "").toLowerCase();
      const matches = query === "" || searchData.includes(query);
      card.style.display = matches ? "" : "none";
      if (matches) visibleCount++;
    });

    // Показываем/скрываем группы целиком
    document.querySelectorAll("#reportGrid > .mb-4").forEach(function (group) {
      const cards = group.querySelectorAll(".report-card");
      const hasVisible = Array.from(cards).some(function (c) {
        return !c.style.display || c.style.display !== "none";
      });
      group.style.display = hasVisible ? "" : "none";
    });

    if (reportCount) {
      if (query === "") {
        reportCount.innerHTML =
          '<i class="bi bi-info-circle"></i> Всего отчетов: ' +
          reportCards.length;
      } else {
        reportCount.innerHTML =
          '<i class="bi bi-info-circle"></i> Найдено: ' +
          visibleCount +
          " из " +
          reportCards.length;
      }
    }
  });
});
