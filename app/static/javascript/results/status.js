document.addEventListener("DOMContentLoaded", () => {
  fetchJobs(userJobs);
});

async function checkJobStatus(job) {
  const spinner = document.getElementById(`${job.job_id}Fetch`);
  try {
    await checkStatus(job.job_id, job.job_id, `/reports/${job.file_id}/zip`);
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
