async function assignWork(name, url, data) {
  const alert = document.getElementById(`${name}Danger`);

  let result;
  try {
    const response = await fetch(url, {
      method: "post",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    result = await response.json();
  } catch (error) {
    console.error(error);
    alert.classList.remove("d-none");
  }

  return result;
}
