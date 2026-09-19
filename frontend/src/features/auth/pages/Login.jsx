import React, { useState } from "react";
import { Navigate, useNavigate, Link } from "react-router";
import "../auth.form.scss";
import { useAuth } from "../hooks/useAuth";

const Login = () => {
  const navigate = useNavigate();

  const { loading, handleLogin } = useAuth();

  //two way binding
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = await handleLogin({ email, password });
    if (data) {
      navigate("/");
    }
  };

  if (loading) {
    return <main>Loading....</main>;
  }

  return (
    <main>
      <div className="form-container">
        <h1>Login</h1>

        <form onSubmit={handleSubmit}>
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

          <button className="btn primary-btn">Login</button>
        </form>

        <p>
          Don't have an account? <Link to="/signup">Signup</Link>
        </p>
      </div>
    </main>
  );
};

export default Login;
