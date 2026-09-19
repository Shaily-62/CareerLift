import { useContext, useEffect } from "react";

import { AuthContext } from "../auth.context";

import { signup, login, logout, getMe } from "../services/auth.api";

export const useAuth = () => {
  const context = useContext(AuthContext);

  const { user, setUser, loading, setLoading } = context;

  // Login
  const handleLogin = async ({ email, password }) => {
    setLoading(true);

    try {
      const data = await login({
        email,
        password,
      });

      setUser(data.user);

      return data;
    } catch (err) {
      console.log("Login error:", err.response?.data || err);

      return null;
    } finally {
      setLoading(false);
    }
  };

  // Signup
  const handleSignup = async ({ username, email, password }) => {
    setLoading(true);

    try {
      const data = await signup({
        username,
        email,
        password,
      });

      setUser(data.user);

      return data;
    } catch (err) {
      console.log("Signup error:", err.response?.data || err);

      return null;
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const handleLogout = async () => {
    setLoading(true);

    try {
      await logout();

      setUser(null);
    } catch (err) {
      console.log("Logout error:", err.response?.data || err);
    } finally {
      setLoading(false);
    }
  };

  // Check existing login
  useEffect(() => {
    const getAndSetUser = async () => {
      try {
        const data = await getMe();

        setUser(data.user);
      } catch (err) {
        console.log("Get current user error:", err.response?.data || err);

        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    getAndSetUser();
  }, []);

  return {
    user,
    loading,
    handleLogin,
    handleLogout,
    handleSignup,
  };
};
