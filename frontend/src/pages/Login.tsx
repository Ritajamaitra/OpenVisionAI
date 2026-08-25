import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, ArrowRight, ShieldCheck, Cpu, BarChart3 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await login(username, password);
      navigate("/");
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Login failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">

      {/* =====================================================
          LEFT BRAND / PRODUCT PANEL
          ===================================================== */}

      <div className="login-visual">

        <div className="login-visual-content">

          <div className="login-logo">
            <span className="login-logo-mark">OV</span>

            <div>
              <strong>OpenVisionAI</strong>
              <span>Vision AI Model Platform</span>
            </div>
          </div>


          <div className="login-hero">

            <div className="hero-eyebrow">
              <span className="hero-dot" />
              AI-powered computer vision
            </div>

            <h1>
              Build.
              <br />
              Train.
              <br />
              <span>Deploy Vision AI.</span>
            </h1>

            <p>
              A unified platform to manage datasets, train vision models,
              deploy inference services and monitor model performance.
            </p>

          </div>


          <div className="login-features">

            <div className="login-feature">
              <div className="feature-icon">
                <Cpu size={18} />
              </div>

              <div>
                <strong>Model Management</strong>
                <span>Register and manage vision models</span>
              </div>
            </div>


            <div className="login-feature">
              <div className="feature-icon">
                <BarChart3 size={18} />
              </div>

              <div>
                <strong>Training & Analytics</strong>
                <span>Track training runs and performance</span>
              </div>
            </div>


            <div className="login-feature">
              <div className="feature-icon">
                <ShieldCheck size={18} />
              </div>

              <div>
                <strong>Secure Inference</strong>
                <span>Run and monitor production predictions</span>
              </div>
            </div>

          </div>

        </div>

        <div className="login-grid-pattern" />
        <div className="login-glow login-glow-one" />
        <div className="login-glow login-glow-two" />

      </div>


      {/* =====================================================
          RIGHT LOGIN PANEL
          ===================================================== */}

      <div className="login-form-section">

        <div className="login-form-container">

          <div className="mobile-login-brand">
            <span className="login-logo-mark">OV</span>
            <strong>OpenVisionAI</strong>
          </div>


          <div className="login-heading">

            <h2>Welcome back</h2>

            <p>
              Sign in to continue to your OpenVisionAI workspace.
            </p>

          </div>


          <form
            className="login-form"
            onSubmit={handleSubmit}
          >

            {/* Username */}

            <div className="form-field">

              <label htmlFor="username">
                Email
              </label>

              <input
                id="username"
                type="email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="you@company.com"
                autoComplete="username"
                required
              />

            </div>


            {/* Password */}

            <div className="form-field">

              <label htmlFor="password">
                Password
              </label>

              <div className="password-wrapper">

                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword((current) => !current)
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>

              </div>

            </div>


            {/* Error */}

            {error && (
              <div className="login-error">
                {error}
              </div>
            )}


            {/* Submit */}

            <button
              type="submit"
              className="login-submit"
              disabled={loading}
            >

              {loading ? (
                <span className="login-loading">
                  <span className="spinner" />
                  Signing in...
                </span>
              ) : (
                <>
                  Sign in
                  <ArrowRight size={18} />
                </>
              )}

            </button>

          </form>


          <div className="login-security">

            <ShieldCheck size={16} />

            <span>
              Secure access to your vision AI workspace
            </span>

          </div>


          <div className="login-footer">
            OpenVisionAI · Vision AI Model Platform
          </div>

        </div>

      </div>

    </div>
  );
}