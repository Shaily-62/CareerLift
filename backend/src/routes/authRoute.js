const { Router } = require("express");
const authController = require("../controllers/authController");
const { authUser } = require("../middleware/authMiddleware");

const authRouter = Router();

/**
 * @route POST /api/auth/signup
 * @description Register a new User
 * @access Public
 */
authRouter.post("/signup", authController.registerUserController);

/**
 * @route POST /api/auth/login
 * @description user login with email and password
 * @access public
 */
authRouter.post("/login", authController.loginUserController);

/**
 * @route GET /api/auth/logout
 * @description clear token from user cookie and add the token in blacklist
 * @access public
 */
authRouter.get("/logout", authController.logoutUserController);

/**
 * @route Get /api/auth/get-me
 * @descriptionget the current logged in user details
 * @access private
 */

authRouter.get("/get-me", authUser, authController.getMeUserController);

module.exports = authRouter;
