const mongoose = require("mongoose");
//this model is used to store the blacklisted token in the database so that it can be used to check if the token is valid or not.
// and also to check if the token is expired or not. if the token is expired then it will be removed from the database.

const blacklistTokenSchema = new mongoose.Schema(
  {
    token: {
      type: String,
      required: [true, "token is required to be added in blacklist"],
    },
  },
  {
    timestamps: true,
  },
);

const blacklistTokenModel = mongoose.model(
  "blacklistToken",
  blacklistTokenSchema,
);

module.exports = blacklistTokenModel;
