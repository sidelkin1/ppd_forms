document.addEventListener("DOMContentLoaded", () => {
  fetchJobs(userJobs);
});

async function checkJobStatus(job) {
  const spinner = document.getElementById(`${job.job_id}Fetch`);
  const resultURL = `/reports/${job.file_id}/zip`;
  try {
    const current = await fetchJobStatus(job.job_id);
    if (current.job.status === "in_progress") {
      await checkStatus(job.job_id, job.job_id, resultURL);
    } else {
      renderJobResponse(job.job_id, current, resultURL);
    }
  } catch (error) {
    console.error(error);
    showDefaultFormAlert(job.job_id);
  } finally {
    spinner.classList.add("d-none");
  }
}

async function fetchJobs(userJobs) {
  try {
    await Promise.all(userJobs.map((job) => checkJobStatus(job)));
  } catch (error) {
    console.error("Error:", error);
  }
}
