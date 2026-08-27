import {
  BarChart3,
  Database,
  FolderKanban,
  Brain,
  Activity,
  Rocket,
  ScanSearch,
  History,
  Settings,
  LogOut,
} from "lucide-react";

import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const navigation = [
  {
    label: "Dashboard",
    path: "/",
    icon: BarChart3,
  },
  {
    label: "Projects",
    path: "/projects",
    icon: FolderKanban,
  },
  {
    label: "Datasets",
    path: "/datasets",
    icon: Database,
  },
  {
    label: "Models",
    path: "/models",
    icon: Brain,
  },
  {
    label: "Training",
    path: "/training",
    icon: Activity,
  },
  {
    label: "Deployments",
    path: "/deployments",
    icon: Rocket,
  },
  {
    label: "Inference",
    path: "/inference",
    icon: ScanSearch,
  },
  {
    label: "History",
    path: "/history",
    icon: History,
  },
];

export default function Sidebar() {
  const { logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">
          OV
        </div>

        <div>
          <strong>OpenVisionAI</strong>
          <span>Vision AI Platform</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigation.map(
          ({
            label,
            path,
            icon: Icon,
          }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `nav-item ${
                  isActive ? "active" : ""
                }`
              }
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          )
        )}
      </nav>

      <div className="sidebar-bottom">
        <NavLink
          to="/settings"
          className="nav-item"
        >
          <Settings size={18} />
          <span>Settings</span>
        </NavLink>

        <button
          className="nav-item logout-button"
          onClick={logout}
        >
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}