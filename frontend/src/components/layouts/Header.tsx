import { Bell } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Header() {
  const { user } = useAuth();

  return (
    <header className="header">
      <div>
        <h2>OpenVisionAI</h2>
      </div>

      <div className="header-actions">
        <button className="icon-button">
          <Bell size={19} />
        </button>

        <div className="user-profile">
          <div className="avatar">
            {user?.username
              ?.charAt(0)
              .toUpperCase()}
          </div>

          <div>
            <strong>{user?.username}</strong>
            <span>{user?.role}</span>
          </div>
        </div>
      </div>
    </header>
  );
}