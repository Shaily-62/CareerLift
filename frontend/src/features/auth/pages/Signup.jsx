
import React, { useState } from "react";
import { useNavigate, Link } from "react-router";
import "../auth.form.scss";
import { useAuth } from "../hooks/useAuth";

const Signup = () => {
  const navigate = useNavigate();

  // Form state
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Auth hook
  const { loading, handleSignup } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check password and confirm password
    if (password !== confirmPassword) {
      alert("Password does not match with confirm password");
      return;
    }

    // Send only the actual password to backend
    const data = await handleSignup({
      username,
      email,
      password,
    });

    if (data) {
      navigate("/");
    }
  };

  // Loading UI
  if (loading) {
    return (
      <main>
        <h1>Loading.....</h1>
      </main>
    );
  }

  return (
    <main>
      <div className="form-container">
        <h1>Signup</h1>

        <form onSubmit={handleSubmit}>
          <div className="input-grp">
            <label htmlFor="username">Username</label>

            <input
              onChange={(e) => {
                setUsername(e.target.value);
              }}
              type="text"
              name="username"
              id="username"
              placeholder="Enter your username"
            />
          </div>

          <div className="input-grp">
            <label htmlFor="email">Your email</label>

            <input
              onChange={(e) => {
                setEmail(e.target.value);
              }}
              type="email"
              name="email"
              id="email"
              placeholder="Enter your email address"
            />
          </div>

          <div className="input-grp">
            <label htmlFor="password">Password</label>

            <input
              onChange={(e) => {
                setPassword(e.target.value);
              }}
              type="password"
              name="password"
              id="password"
              placeholder="Enter your password"
            />
          </div>

          <div className="input-grp">
            <label htmlFor="confirm-password">Confirm Password</label>

            <input
              onChange={(e) => {
                setConfirmPassword(e.target.value);
              }}
              type="password"
              name="confirmPassword"
              id="confirm-password"
              placeholder="Confirm your password"
            />
          </div>

          <button type="submit" className="btn primary-btn">
            Signup
          </button>
        </form>

        <p>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </main>
  );
};

export default Signup;

