async function fetchReservoirs(report, path) {
  const uniqueKey = `${report}Reservoirs`;
  const currentRequestId = setRequestId(uniqueKey);
  const loader = document.getElementById(`${report}Fetch`);
  const { value: fieldID } = document.getElementById(`${report}Fields`);
  const reservoirsList = document.getElementById(`${report}Reservoirs`);
  reservoirsList.replaceChildren(reservoirsList[0]);

  loader.classList.remove("d-none");

  try {
    const response = await fetchWithAuth(
      buildUrl(`/uneft/fields/${fieldID}/${path}`)
    );
    if (!response.ok || currentRequestId !== getRequestId(uniqueKey)) {
      return;
    }
    const reservoirs = await response.json();
    if (currentRequestId === getRequestId(uniqueKey)) {
      reservoirs.forEach(({ id, name }) => {
        let option = document.createElement("option");
        option.value = id;
        option.text = name;
        reservoirsList.add(option);
      });
    }
  } catch (error) {
    console.error(error);
  } finally {
    if (currentRequestId === getRequestId(uniqueKey)) {
      loader.classList.add("d-none");
    }
  }
}
