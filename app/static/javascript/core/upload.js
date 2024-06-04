async function sendFile(file, url) {
  if (!file) {
    return null;
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(url, {
    method: "post",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return await response.json();
}

async function sendMultipleFiles(files, url) {
  return await Promise.all(files.map((file) => sendFile(file, url)));
}
