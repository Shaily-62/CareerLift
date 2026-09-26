const express = require("express");
const authMiddleware = require("../middleware/authMiddleware");
const interviewController = require("../controllers/interviewController");
const upload = require("../middleware/fileMiddleware");

const interviewRouter = express.Router();

/**
 * @route post /api/interview/
 * @description generate new interview report an the basis ofuserself description , resume pdf and job description
 * @access private
 */
interviewRouter.post(
  "/",
  authMiddleware.authUser,
  upload.single("resume"),
  interviewController.generateInterviewReportController,
);

module.exports = interviewRouter;
