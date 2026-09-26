const pdfParse = require("pdf-parse");

const { generateInterviewReport } = require("../services/aiServices");

const interviewReportModel = require("../models/interviewReportModel");

async function generateInterviewReportController(req, res) {
  try {
    const resumeFile = req.file;

    const { selfDescription, jobDescription } = req.body;

    // Validate text fields
    if (!jobDescription?.trim()) {
      return res.status(400).json({
        message: "Job description is required",
      });
    }

    if (!selfDescription?.trim()) {
      return res.status(400).json({
        message: "Self description is required",
      });
    }

    // Validate uploaded file
    if (!resumeFile) {
      return res.status(400).json({
        message: "Resume PDF is required",
      });
    }

    if (resumeFile.mimetype !== "application/pdf") {
      return res.status(400).json({
        message: "Only PDF files are allowed",
      });
    }

    // Extract text from PDF
    const pdfResult = await new pdfParse.PDFParse(
      Uint8Array.from(resumeFile.buffer),
    ).getText();

    const resumeContent = pdfResult.text;

    if (!resumeContent?.trim()) {
      return res.status(400).json({
        message: "Could not extract text from the resume",
      });
    }

    // Generate AI report
    const interviewReportByAi = await generateInterviewReport({
      resume: resumeContent,
      selfDescription,
      jobDescription,
    });

    // Save report in MongoDB
    const interviewReport = await interviewReportModel.create({
      user: req.user.id,
      resumeText: resumeContent,
      selfDescription,
      jobDescription,
      ...interviewReportByAi,
    });

    return res.status(201).json({
      message: "Interview report generated successfully",
      reportId: interviewReport._id,
      report: interviewReport,
    });
  } catch (error) {
    console.error("Generate interview report error:", error);

    return res.status(500).json({
      message: "Failed to generate interview report",
      error: process.env.NODE_ENV === "development" ? error.message : undefined,
    });
  }
}

module.exports = {
  generateInterviewReportController,
};
