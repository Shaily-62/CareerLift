import React, { useState } from "react";
import "../style/Home.scss";

import {
  generateInterviewReport,
} from "../services/interview.api";

const Home = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [selfDescription, setSelfDescription] = useState("");
  const [resume, setResume] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleResumeChange = (e) => {
    const file = e.target.files[0];

    setError("");
    setSuccess("");

    if (!file) {
      setResume(null);
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Please upload a PDF file only.");
      setResume(null);
      return;
    }

    if (file.size > 3 * 1024 * 1024) {
      setError("Resume size should not exceed 3 MB.");
      setResume(null);
      return;
    }

    setResume(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!jobDescription.trim()) {
      setError("Please enter the job description.");
      return;
    }

    if (!resume) {
      setError("Please upload your resume.");
      return;
    }

    if (!selfDescription.trim()) {
      setError("Please enter your self-description.");
      return;
    }

    try {
      setLoading(true);

      const data = await generateInterviewReport({
        jobDescription,
        selfDescription,
        resume,
      });

      console.log("Interview report:", data);

      setSuccess(
        "Interview report generated successfully!"
      );

      console.log("Report ID:", data.reportId);
    } catch (error) {
      console.error("Generate report error:", error);

      setError(
        error.message || "Failed to generate interview report."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="home">
      <form
        className="home-form"
        onSubmit={handleSubmit}
      >
        <div className="left">
          <label htmlFor="jobDescription">
            Job Description
          </label>

          <textarea
            id="jobDescription"
            name="jobDescription"
            placeholder="Enter job description here..."
            value={jobDescription}
            onChange={(e) =>
              setJobDescription(e.target.value)
            }
          />
        </div>

        <div className="right">
          <div className="input-grp">
            <label htmlFor="resume">
              Upload Resume (PDF)
            </label>

            <input
              type="file"
              id="resume"
              name="resume"
              accept=".pdf,application/pdf"
              onChange={handleResumeChange}
            />

            {resume && (
              <p className="file-name">
                Selected: {resume.name}
              </p>
            )}
          </div>

          <div className="input-grp">
            <label htmlFor="selfDescription">
              Self Description
            </label>

            <textarea
              id="selfDescription"
              name="selfDescription"
              placeholder="Describe yourself in a few sentences..."
              value={selfDescription}
              onChange={(e) =>
                setSelfDescription(e.target.value)
              }
            />
          </div>

          {error && (
            <p className="error-message">
              {error}
            </p>
          )}

          {success && (
            <p className="success-message">
              {success}
            </p>
          )}

          <button
            type="submit"
            className="generate-btn"
            disabled={loading}
          >
            {loading
              ? "Generating Report..."
              : "Generate Interview Report"}
          </button>
        </div>
      </form>
    </main>
  );
};

export default Home;