const userModel = require("../models/userModel");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const blacklistTokenModel = require("../models/blacklistModel");

/**
 * @name registerUserController
 * @description Registera new user ,expects username,email,password
 * @access Public
 */
async function registerUserController(req, res) {
  const { username, email, password } = req.body;

  //cheacking empty fields
  if (!username || !email || !password) {
    return res.status(400).json({
      message: "Please provide usename, email, password",
    });
  }

  //checking is user exist
  const isUserAlreadyExist = await userModel.findOne({
    $or: [{ username }, { email }],
  });

  if (isUserAlreadyExist) {
    return res.status(400).json({
      message: "Account already exists with this email addressor username",
    });
  }

  //hashing the password
  const hashPassword = await bcrypt.hash(password, 10);

  //creating the new user
  const user = await userModel.create({
    username,
    email,
    password: hashPassword,
  });

  //generating the token ewith the help of jwt
  const token = jwt.sign(
    { id: user._id, username: user.username },
    process.env.JWT_SECRET,
    { expiresIn: "1d" },
  );

  //settinig the cookies
  res.cookie("token", token);

  res.status(201).json({
    message: "Successfully user Created",
    user: {
      id: user._id,
      username: user.username,
      email: user.email,
    },
  });
}

/**
 * @name loginUserController
 * @description login a user , expects email,password
 * @access public
 */

async function loginUserController(req, res) {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: "ALl fields required" });
  }

  const user = await userModel.findOne({ email });

  if (!user) {
    return res.status(400).json({ message: "Invalid email or password!" });
  }

  //if user found
  const isPasswordValid = await bcrypt.compare(password, user.password);

  if (!isPasswordValid) {
    return res.status(400).json({
      message: "Invaild email or Password",
    });
  }

  const token = jwt.sign(
    { id: user._id, username: user.username },
    process.env.JWT_SECRET,
    { expiresIn: "1d" },
  );

  res.cookie("token", token);

  res.status(200).json({
    message: "user loggedIn Successfully",
    user: {
      id: user._id,
      username: user.username,
      email: user.email,
    },
  });
}

/**
 * @name logoutUserController
 * @description clear token from user cookie and add the token in blacklist
 * @access public
 */

async function logoutUserController(req, res) {
  const token = req.cookies.token;

  if (token) {
    await blacklistTokenModel.create({ token });
  }

  res.clearCookie("token");
  res.status(200).json({ message: "User Logout Successfully" });
}

/**
 * 
 *@name getMeUserController
 @description get the current logged in user details
 @access private
 */
async function getMeUserController(req, res) {
  const user = await userModel.findById(req.user.id);

  if (!user) {
    return res.status(404).json({ message: "User not found" });
  }

  res.status(200).json({
    message: "User details fetched successfully",
    user: {
      id: user._id,
      username: user.username,
      email: user.email,
    },
  });
}

module.exports = {
  registerUserController,
  loginUserController,
  logoutUserController,
  getMeUserController,
};
