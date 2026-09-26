require("dotenv").config();
const connectDB = require("./src/config/database");
const app = require("./src/app");
const invoke = require("./src/services/aiServices");

const dns = require("dns");
dns.setServers(["8.8.8.8", "8.8.4.4"]);
connectDB();


app.listen(process.env.PORT || 3000, () => {
  console.log("Server is running on port " + (process.env.PORT || 3000));
});
