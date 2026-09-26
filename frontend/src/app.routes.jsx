import { createBrowserRouter } from "react-router";

import Login from "./features/auth/pages/Login";
import Signup from "./features/auth/pages/Signup";
import Protected from "./features/auth/components/Protected";
import Home from "./features/interview/pages/Home"

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/signup",
    element: <Signup />,
  },
  {
    path: "/",
    element: (
      <Protected>
        <Home/>
      </Protected>
    ),
  },
]);
