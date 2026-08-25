import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";

import ProtectedRoute
  from "./components/common/ProtectedRoute";

import AppLayout
  from "./components/layouts/AppLayout";

import Login
  from "./pages/Login";

import Dashboard
  from "./pages/Dashboard";

import Projects
  from "./pages/Projects";

import Datasets
  from "./pages/Datasets";

import Annotations
  from "./pages/Annotations";

import Models
  from "./pages/Models";

import Training
  from "./pages/Training";

import Deployments
  from "./pages/Deployments";

import Inference
  from "./pages/Inference";

import InferenceHistory
  from "./pages/InferenceHistory";

import NotFound
  from "./pages/NotFound";


function App() {

  return (

    <BrowserRouter>

      <AuthProvider>

        <Routes>

          {/* ====================================================
              PUBLIC
              ==================================================== */}

          <Route
            path="/login"
            element={<Login />}
          />


          {/* ====================================================
              PROTECTED APPLICATION
              ==================================================== */}

          <Route
            element={<ProtectedRoute />}
          >

            <Route
              element={<AppLayout />}
            >

              {/* Dashboard */}

              <Route
                path="/"
                element={<Dashboard />}
              />


              {/* Projects */}

              <Route
                path="/projects"
                element={<Projects />}
              />


              {/* Datasets */}

              <Route
                path="/datasets"
                element={<Datasets />}
              />


              {/* Annotation Workspace */}

              <Route
                path="/datasets/:datasetId/annotations"
                element={<Annotations />}
              />


              {/* Models */}

              <Route
                path="/models"
                element={<Models />}
              />


              {/* Training */}

              <Route
                path="/training"
                element={<Training />}
              />


              {/* Deployments */}

              <Route
                path="/deployments"
                element={<Deployments />}
              />


              {/* Inference */}

              <Route
                path="/inference"
                element={<Inference />}
              />


              {/* History */}

              <Route
                path="/history"
                element={<InferenceHistory />}
              />

            </Route>

          </Route>


          {/* ====================================================
              FALLBACK
              ==================================================== */}

          <Route
            path="*"
            element={<NotFound />}
          />

        </Routes>

      </AuthProvider>

    </BrowserRouter>
  );
}


export default App;