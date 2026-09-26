const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:3000";

export const generateInterviewReport = async ({
  jobDescription,
  selfDescription,
  resume,
}) => {
  const formData = new FormData();

  formData.append("jobDescription", jobDescription);
  formData.append("selfDescription", selfDescription);
  formData.append("resume", resume);

  const response = await fetch(`${API_URL}/api/interview/`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  let data;

  try {
    data = await response.json();
  } catch (error) {
    throw new Error("Invalid response received from server.");
  }

  if (!response.ok) {
    throw new Error(
      data.message || "Failed to generate interview report."
    );
  }

  return data;
};