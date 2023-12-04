async function sendFile(name, url) {
  const alert = document.getElementById(`${name}Danger`);

  const file = document.getElementById(`${name}File`).files[0];
  const formData = new FormData();
  formData.append("file", file);

  let result;
  try {
    const response = await fetch(url, {
      method: "post",
      body: formData,
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
