async function assignWork(name, url, data) {
  resetFormAlert(name);
  clearFormErrors(name);
  if (!validateForm(name)) {
    showFormAlert(name, "Заполните обязательные поля");
    return;
  }

  try {
    const response = await fetchWithAuth(buildUrl(url), {
      method: "post",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (response.status === 422) {
      const payload = await response.json().catch(() => null);
      handleValidationErrors(name, payload);
      return;
    }
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(error);
    showDefaultFormAlert(name);
  }
}
