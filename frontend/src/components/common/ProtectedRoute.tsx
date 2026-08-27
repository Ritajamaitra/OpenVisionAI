import {
  Navigate,
  Outlet,
  useLocation,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";


export default function ProtectedRoute() {

  const {
    isAuthenticated,
    authLoading,
  } = useAuth();

  const location =
    useLocation();


  /* ==========================================================
     AUTH STATE IS STILL BEING RESTORED
     ========================================================== */

  if (authLoading) {

    return (

      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#f5f7fb",
          color: "#667085",
          fontFamily:
            "Inter, system-ui, sans-serif",
          fontSize: "14px",
        }}
      >

        Loading OpenVisionAI...

      </div>

    );

  }


  /* ==========================================================
     NOT AUTHENTICATED
     ========================================================== */

  if (!isAuthenticated) {

    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location,
        }}
      />
    );

  }


  /* ==========================================================
     AUTHENTICATED
     ========================================================== */

  return <Outlet />;

}