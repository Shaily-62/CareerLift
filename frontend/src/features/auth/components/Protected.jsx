import React from "react";
import { useAuth } from "../hooks/useAuth";
import { Navigate } from "react-router";

const Protected = ({ children }) => {
  const { loading, user } = useAuth();

  if (loading) {
    return (
      <main>
        <h1>Loading....</h1>
      </main>
    );
  }

  //checking if user login or not
  if (!user) {
    // alert("login required")
    return <Navigate to= "/login" />;
  }

  return children;
};

export default Protected;
