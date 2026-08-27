import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  Cpu,
  BarChart3,
  RefreshCw,
  ArrowLeft,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import {
  register as registerUser,
  generateResetCaptcha,
  resetPassword,
} from "../api/auth";

type ViewMode = "login" | "register" | "forgot";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [view, setView] = useState<ViewMode>("login");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [fullName, setFullName] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerUsername, setRegisterUsername] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [resetEmail, setResetEmail] = useState("");
  const [captcha, setCaptcha] = useState("");
  const [captchaInput, setCaptchaInput] = useState("");
  const [captchaVerified, setCaptchaVerified] = useState(false);
  const [resetNewPassword, setResetNewPassword] = useState("");
  const [resetConfirmPassword, setResetConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const switchView = (nextView: ViewMode) => {
    setView(nextView);
    setError("");
    setSuccess("");
    setCaptcha("");
    setCaptchaInput("");
    setCaptchaVerified(false);
  };

  const handleLogin = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");
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

  const handleRegister = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (registerPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (registerPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await registerUser({
        username: registerUsername.trim(),
        email: registerEmail.trim(),
        full_name: fullName.trim(),
        password: registerPassword,
      });

      setSuccess("Account created successfully. You can now sign in.");
      setUsername(registerEmail.trim());
      setPassword("");
      setView("login");
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Unable to create the account. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCaptcha = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setCaptcha("");
    setCaptchaInput("");
    setCaptchaVerified(false);

    if (!resetEmail.trim()) {
      setError("Please enter your email address.");
      return;
    }

    setLoading(true);

    try {
      const response = await generateResetCaptcha(resetEmail.trim());
      setCaptcha(response.captcha);
      setSuccess("Security check generated. Enter the CAPTCHA below.");
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Unable to generate the security check."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCaptcha = () => {
    setError("");
    setSuccess("");

    if (!captcha || captchaInput.trim().toUpperCase() !== captcha) {
      setCaptchaVerified(false);
      setError("Incorrect CAPTCHA. Please try again.");
      return;
    }

    setCaptchaVerified(true);
    setSuccess("CAPTCHA verified. You can now set a new password.");
  };

  const handleResetPassword = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!captchaVerified) {
      setError("Please verify the CAPTCHA first.");
      return;
    }

    if (resetNewPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (resetNewPassword !== resetConfirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await resetPassword(
        resetEmail.trim(),
        captchaInput.trim().toUpperCase(),
        resetNewPassword
      );

      setSuccess("Password reset successfully. You can now sign in.");
      setPassword("");
      setResetNewPassword("");
      setResetConfirmPassword("");
      setCaptcha("");
      setCaptchaInput("");
      setCaptchaVerified(false);
      setView("login");
      setUsername(resetEmail.trim());
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Unable to reset the password. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const pageTitle =
    view === "login"
      ? "Welcome back"
      : view === "register"
        ? "Create your account"
        : "Reset your password";

  const pageSubtitle =
    view === "login"
      ? "Sign in to continue to your OpenVisionAI workspace."
      : view === "register"
        ? "Create an account to access your OpenVisionAI workspace."
        : "Verify the security check to create a new password.";

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
          RIGHT AUTHENTICATION PANEL
          ===================================================== */}

      <div className="login-form-section">
        <div className="login-form-container">

          <div className="mobile-login-brand">
            <span className="login-logo-mark">OV</span>
            <strong>OpenVisionAI</strong>
          </div>

          <div className="login-heading">
            <h2>{pageTitle}</h2>
            <p>{pageSubtitle}</p>
          </div>

          {view === "login" && (
            <>
              <form className="login-form" onSubmit={handleLogin}>

                <div className="form-field">
                  <label htmlFor="username">Email</label>

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

                <div className="form-field">
                  <label htmlFor="password">Password</label>

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
                        showPassword ? "Hide password" : "Show password"
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

                {error && <div className="login-error">{error}</div>}
                {success && (
                  <div
                    className="login-success"
                    style={{
                      padding: "10px 12px",
                      borderRadius: 8,
                      marginBottom: 12,
                      fontSize: 13,
                    }}
                  >
                    {success}
                  </div>
                )}

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

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 16,
                  marginTop: 18,
                  fontSize: 13,
                }}
              >
                <button
                  type="button"
                  onClick={() => switchView("forgot")}
                  style={{
                    background: "none",
                    padding: 0,
                    cursor: "pointer",
                    color: "#3168ff",
                    fontWeight: 600,
                  }}
                >
                  Forgot password?
                </button>

                <button
                  type="button"
                  onClick={() => switchView("register")}
                  style={{
                    background: "none",
                    padding: 0,
                    cursor: "pointer",
                    color: "#3168ff",
                    fontWeight: 600,
                  }}
                >
                  Create an account
                </button>
              </div>
            </>
          )}

          {view === "register" && (
            <form className="login-form" onSubmit={handleRegister}>

              <div className="form-field">
                <label htmlFor="full-name">Full name</label>
                <input
                  id="full-name"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                  autoComplete="name"
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="register-email">Email</label>
                <input
                  id="register-email"
                  type="email"
                  value={registerEmail}
                  onChange={(e) => setRegisterEmail(e.target.value)}
                  placeholder="you@company.com"
                  autoComplete="email"
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="register-username">Username</label>
                <input
                  id="register-username"
                  type="text"
                  value={registerUsername}
                  onChange={(e) => setRegisterUsername(e.target.value)}
                  placeholder="Choose a username"
                  autoComplete="username"
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="register-password">Password</label>

                <div className="password-wrapper">
                  <input
                    id="register-password"
                    type={showRegisterPassword ? "text" : "password"}
                    value={registerPassword}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    autoComplete="new-password"
                    minLength={8}
                    required
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() =>
                      setShowRegisterPassword((current) => !current)
                    }
                    aria-label={
                      showRegisterPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    {showRegisterPassword ? (
                      <EyeOff size={18} />
                    ) : (
                      <Eye size={18} />
                    )}
                  </button>
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="confirm-password">Confirm password</label>
                <input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your password"
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
              </div>

              {error && <div className="login-error">{error}</div>}
              {success && (
                <div
                  className="login-success"
                  style={{
                    padding: "10px 12px",
                    borderRadius: 8,
                    marginBottom: 12,
                    fontSize: 13,
                  }}
                >
                  {success}
                </div>
              )}

              <button
                type="submit"
                className="login-submit"
                disabled={loading}
              >
                {loading ? (
                  <span className="login-loading">
                    <span className="spinner" />
                    Creating account...
                  </span>
                ) : (
                  <>
                    Create account
                    <ArrowRight size={18} />
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => switchView("login")}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 6,
                  width: "100%",
                  marginTop: 12,
                  background: "none",
                  cursor: "pointer",
                  color: "#667085",
                  fontSize: 13,
                  fontWeight: 600,
                }}
              >
                <ArrowLeft size={15} />
                Back to sign in
              </button>
            </form>
          )}

          {view === "forgot" && (
            <>
              {!captcha && !captchaVerified && (
                <form
                  className="login-form"
                  onSubmit={handleGenerateCaptcha}
                >
                  <div className="form-field">
                    <label htmlFor="reset-email">Email</label>
                    <input
                      id="reset-email"
                      type="email"
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      placeholder="you@company.com"
                      autoComplete="email"
                      required
                    />
                  </div>

                  {error && <div className="login-error">{error}</div>}
                  {success && (
                    <div
                      className="login-success"
                      style={{
                        padding: "10px 12px",
                        borderRadius: 8,
                        marginBottom: 12,
                        fontSize: 13,
                      }}
                    >
                      {success}
                    </div>
                  )}

                  <button
                    type="submit"
                    className="login-submit"
                    disabled={loading}
                  >
                    {loading ? (
                      <span className="login-loading">
                        <span className="spinner" />
                        Generating...
                      </span>
                    ) : (
                      <>
                        Continue
                        <ArrowRight size={18} />
                      </>
                    )}
                  </button>
                </form>
              )}

              {captcha && !captchaVerified && (
                <div className="login-form">

                  <div className="form-field">
                    <label>Security check</label>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                      }}
                    >
                      <div
                        style={{
                          flex: 1,
                          minHeight: 52,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          border: "1px solid #d7ddea",
                          borderRadius: 9,
                          background: "#f7f9fc",
                          fontSize: 22,
                          fontWeight: 800,
                          letterSpacing: 5,
                          userSelect: "none",
                        }}
                      >
                        {captcha}
                      </div>

                      <button
                        type="button"
                        onClick={() => {
                          setCaptcha("");
                          setCaptchaInput("");
                          setCaptchaVerified(false);
                          setSuccess("");
                          setError("");
                        }}
                        title="Generate a new CAPTCHA"
                        aria-label="Generate a new CAPTCHA"
                        style={{
                          width: 44,
                          height: 44,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          border: "1px solid #d7ddea",
                          borderRadius: 9,
                          background: "#fff",
                          cursor: "pointer",
                          color: "#53627a",
                        }}
                      >
                        <RefreshCw size={17} />
                      </button>
                    </div>
                  </div>

                  <div className="form-field">
                    <label htmlFor="captcha-input">Enter CAPTCHA</label>
                    <input
                      id="captcha-input"
                      type="text"
                      value={captchaInput}
                      onChange={(e) =>
                        setCaptchaInput(e.target.value.toUpperCase())
                      }
                      placeholder="Enter the code above"
                      autoComplete="off"
                      maxLength={6}
                      required
                    />
                  </div>

                  {error && <div className="login-error">{error}</div>}
                  {success && (
                    <div
                      className="login-success"
                      style={{
                        padding: "10px 12px",
                        borderRadius: 8,
                        marginBottom: 12,
                        fontSize: 13,
                      }}
                    >
                      {success}
                    </div>
                  )}

                  <button
                    type="button"
                    className="login-submit"
                    onClick={handleVerifyCaptcha}
                  >
                    Verify CAPTCHA
                    <ShieldCheck size={18} />
                  </button>
                </div>
              )}

              {captchaVerified && (
                <form className="login-form" onSubmit={handleResetPassword}>

                  <div className="form-field">
                    <label htmlFor="reset-new-password">New password</label>

                    <div className="password-wrapper">
                      <input
                        id="reset-new-password"
                        type={showResetPassword ? "text" : "password"}
                        value={resetNewPassword}
                        onChange={(e) => setResetNewPassword(e.target.value)}
                        placeholder="At least 8 characters"
                        autoComplete="new-password"
                        minLength={8}
                        required
                      />

                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() =>
                          setShowResetPassword((current) => !current)
                        }
                        aria-label={
                          showResetPassword
                            ? "Hide password"
                            : "Show password"
                        }
                      >
                        {showResetPassword ? (
                          <EyeOff size={18} />
                        ) : (
                          <Eye size={18} />
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="form-field">
                    <label htmlFor="reset-confirm-password">
                      Confirm password
                    </label>
                    <input
                      id="reset-confirm-password"
                      type="password"
                      value={resetConfirmPassword}
                      onChange={(e) =>
                        setResetConfirmPassword(e.target.value)
                      }
                      placeholder="Re-enter your password"
                      autoComplete="new-password"
                      minLength={8}
                      required
                    />
                  </div>

                  {error && <div className="login-error">{error}</div>}
                  {success && (
                    <div
                      className="login-success"
                      style={{
                        padding: "10px 12px",
                        borderRadius: 8,
                        marginBottom: 12,
                        fontSize: 13,
                      }}
                    >
                      {success}
                    </div>
                  )}

                  <button
                    type="submit"
                    className="login-submit"
                    disabled={loading}
                  >
                    {loading ? (
                      <span className="login-loading">
                        <span className="spinner" />
                        Resetting...
                      </span>
                    ) : (
                      <>
                        Reset password
                        <ArrowRight size={18} />
                      </>
                    )}
                  </button>
                </form>
              )}

              <button
                type="button"
                onClick={() => switchView("login")}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 6,
                  width: "100%",
                  marginTop: 14,
                  background: "none",
                  cursor: "pointer",
                  color: "#667085",
                  fontSize: 13,
                  fontWeight: 600,
                }}
              >
                <ArrowLeft size={15} />
                Back to sign in
              </button>
            </>
          )}

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
