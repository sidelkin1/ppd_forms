async function fetchFields(report, path) {
  const loader = document.getElementById(`${report}Fetch`);
  const fieldList = document.getElementById(`${report}Fields`);

  loader.classList.remove("d-none");

  try {
    const response = await fetch(buildUrl(`/uneft/${path}`));
    if (!response.ok) {
      return;
    }
    const fields = await response.json();
    fields.forEach(({ id, name }) => {
      let option = document.createElement("option");
      option.value = id;
      option.text = name;
      fieldList.add(option);
    });
  } catch (error) {
    console.error(error);
  } finally {
    loader.classList.add("d-none");
  }
}

async function loadReportFields(reportFields) {
  try {
    await Promise.all(
      reportFields.map(([report, path]) => fetchFields(report, path))
    );
  } catch (error) {
    console.error("Error:", error);
  }
}

loadReportFields([
  ["fnv", "fields?stock=injection"],
  ["matbal", "fields?stock=production"],
]);
