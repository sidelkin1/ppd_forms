async function fetchDates(path, source) {
  const loader = document.getElementById(`${path}Fetch`);
  const dates = document.getElementById(`${path}Dates`);

  loader.classList.remove("d-none");

  try {
    const response = await fetch(`/${source}/${path}`);
    if (!response.ok) {
      return;
    }
    const { min_date, max_date } = await response.json();
    dates.textContent = [
      new Date(min_date).toLocaleDateString(),
      new Date(max_date).toLocaleDateString(),
    ].join(" • ");
  } catch (error) {
    console.error(error);
  } finally {
    loader.classList.add("d-none");
  }
}

async function loadTableDates(tableURLs) {
  try {
    await Promise.all(
      tableURLs.map(({ path, source }) => fetchDates(path, source))
    );
  } catch (error) {
    console.error("Error:", error);
  }
}

loadTableDates(dbTables);
