const mongoose = require("mongoose");

// Technical question schema
const technicalQuestionSchema = new mongoose.Schema(
  {
    question: {
      type: String,
      required: [true, "Technical question is required"],
    },

    intention: {
      type: String,
      required: [true, "Intention is required"],
    },

    answer: {
      type: String,
      required: [true, "Answer is required"],
    },
  },
  {
    _id: false,
  },
);

// Behavioral question schema
const behavioralQuestionSchema = new mongoose.Schema(
  {
    question: {
      type: String,
      required: [true, "Behavioral question is required"],
    },

    intention: {
      type: String,
      required: [true, "Intention is required"],
    },

    answer: {
      type: String,
      required: [true, "Answer is required"],
    },
  },
  {
    _id: false,
  },
);

// Skill gap schema
const skillGapsSchema = new mongoose.Schema(
  {
    skill: {
      type: String,
      required: [true, "Skill is required"],
    },

    severity: {
      type: String,
      enum: ["low", "medium", "high"],
      required: [true, "Severity is required"],
    },
  },
  {
    _id: false,
  },
);

// Preparation plan schema
const preparationPlanSchema = new mongoose.Schema(
  {
    day: {
      type: Number,
      required: [true, "Day is required"],
      min: 1,
    },

    focus: {
      type: String,
      required: [true, "Focus is required"],
    },

    tasks: [
      {
        type: String,
        required: [true, "Task is required"],
      },
    ],
  },
  {
    _id: false,
  },
);

// Main interview report schema
const interviewReportSchema = new mongoose.Schema(
  {
    jobDescription: {
      type: String,
      required: [true, "Job description is required"],
      trim: true,
    },

    resumeText: {
      type: String,
      required: [true, "Resume text is required"],
    },

    selfDescription: {
      type: String,
      required: [true, "Self description is required"],
      trim: true,
    },

    matchScore: {
      type: Number,
      min: 0,
      max: 100,
      required: true,
    },

    technicalQuestions: {
      type: [technicalQuestionSchema],
      default: [],
    },

    behavioralQuestions: {
      type: [behavioralQuestionSchema],
      default: [],
    },

    skillGaps: {
      type: [skillGapsSchema],
      default: [],
    },

    preparationPlan: {
      type: [preparationPlanSchema],
      default: [],
    },

    title: {
      type: String,
      required: [true, "Report title is required"],
    },

    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "users",
      required: [true, "User is required"],
      index: true,
    },
  },
  {
    timestamps: true,
  },
);

const interviewReportModel = mongoose.model(
  "interviewReport",
  interviewReportSchema,
);

module.exports = interviewReportModel;
