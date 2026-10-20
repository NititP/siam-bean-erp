import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { menuFor } from "../lib/roles";

/** Page frame: the logged-in user, the menu for their role, and log out. */
export default function Layout() {
  const { me, logOut } = useAuth();
  if (!me) return null;

  return (
    <div className="layout">
      <nav className="menu">
        <strong className="brand">Siam Bean</strong>
        <div className="who">
          <span>{me.full_name}</span>
          <span className="muted">{me.role}</span>
        </div>
        {menuFor(me.role).map((item) => (
          <NavLink key={item.path} to={item.path}>
            {item.label}
          </NavLink>
        ))}
        <button className="logout" onClick={logOut}>
          Log out
        </button>
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
