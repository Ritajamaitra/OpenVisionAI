import { useEffect, useState } from "react";
import {
  FolderKanban,
  Database,
  BrainCircuit,
  Activity,
  RefreshCw,
  AlertCircle,
} from "lucide-react";

import {
  getDashboardStats,
  type DashboardStats,
} from "../api/dashboard";

interface StatCard {
  label: string;
  value: number;
  icon: React.ReactNode;
  description: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getDashboardStats();

      setStats(data);
    } catch (err: any) {
      console.error("Failed to load dashboard statistics:", err);

      setError(
        err?.response?.data?.detail ??
          "Unable to load dashboard statistics."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const statCards: StatCard[] = [
    {
      label: "Projects",
      value: stats?.projects ?? 0,
      icon: <FolderKanban size={22} />,
      description: "Active workspace projects",
    },
    {
      label: "Datasets",
      value: stats?.datasets ?? 0,
      icon: <Database size={22} />,
      description: "Managed vision datasets",
    },
    {
      label: "Models",
      value: stats?.models ?? 0,
      icon: <BrainCircuit size={22} />,
      description: "Registered vision models",
    },
    {
      label: "Inference Runs",
      value: stats?.inference_runs ?? 0,
      icon: <Activity size={22} />,
      description: "Inference executions",
    },
  ];

  return (
    <div className="dashboard-page">

      {/* =====================================================
          PAGE HEADER
          ===================================================== */}

      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            OpenVisionAI Platform
          </span>

          <h1>Dashboard</h1>

          <p>
            Monitor your projects, datasets, models and
            inference activity from one place.
          </p>
        </div>

        <button
          className="dashboard-refresh"
          onClick={fetchStats}
          disabled={loading}
          title="Refresh dashboard"
        >
          <RefreshCw
            size={17}
            className={loading ? "spin" : ""}
          />

          <span>
            {loading ? "Refreshing..." : "Refresh"}
          </span>
        </button>
      </div>


      {/* =====================================================
          ERROR
          ===================================================== */}

      {error && (
        <div className="dashboard-error">
          <AlertCircle size={18} />

          <div>
            <strong>Unable to load dashboard</strong>

            <p>{error}</p>
          </div>

          <button onClick={fetchStats}>
            Try again
          </button>
        </div>
      )}


      {/* =====================================================
          KPI CARDS
          ===================================================== */}

      <div className="stats-grid">

        {statCards.map((stat) => (
          <div
            className="stat-card"
            key={stat.label}
          >

            <div className="stat-card-top">

              <div className="stat-icon">
                {stat.icon}
              </div>

              <span className="stat-label">
                {stat.label}
              </span>

            </div>

            <div className="stat-value">
              {loading ? (
                <span className="stat-loading">
                  —
                </span>
              ) : (
                stat.value.toLocaleString()
              )}
            </div>

            <div className="stat-description">
              {stat.description}
            </div>

          </div>
        ))}

      </div>


      {/* =====================================================
          PLATFORM OVERVIEW
          ===================================================== */}

      <div className="dashboard-card">

        <div className="dashboard-card-header">
          <div>
            <span className="card-eyebrow">
              Platform Overview
            </span>

            <h2>Welcome to OpenVisionAI</h2>
          </div>
        </div>

        <p>
          Manage datasets, train and register models,
          deploy inference services and monitor
          inference runs from one platform.
        </p>

        <div className="dashboard-flow">

          <div className="flow-item">
            <span className="flow-number">01</span>

            <div>
              <strong>Datasets</strong>
              <span>
                Manage and organize vision datasets
              </span>
            </div>
          </div>

          <div className="flow-line" />

          <div className="flow-item">
            <span className="flow-number">02</span>

            <div>
              <strong>Models</strong>
              <span>
                Register and manage trained models
              </span>
            </div>
          </div>

          <div className="flow-line" />

          <div className="flow-item">
            <span className="flow-number">03</span>

            <div>
              <strong>Inference</strong>
              <span>
                Execute and monitor predictions
              </span>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}