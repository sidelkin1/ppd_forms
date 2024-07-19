async function fetchReservoirs(report, path) {
  const loader = document.getElementById(`${report}Fetch`);
  const { value: fieldID } = document.getElementById(`${report}Fields`);
  const reservoirsList = document.getElementById(`${report}Reservoirs`);
  reservoirsList.replaceChildren(reservoirsList[0]);

  loader.classList.remove("d-none");

  try {
    const response = await fetch(buildUrl(`/uneft/fields/${fieldID}/${path}`));
    if (!response.ok) {
      return;
    }
    const reservoirs = await response.json();
    reservoirs.forEach(({ id, name }) => {
      let option = document.createElement("option");
      option.value = id;
      option.text = name;
      reservoirsList.add(option);
    });
  } catch (error) {
    console.error(error);
  } finally {
    loader.classList.add("d-none");
  }
}
