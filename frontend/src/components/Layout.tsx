import { NavLink, Outlet } from "react-router-dom";
import { menuFor, type Role } from "../lib/roles";

/** Page frame with the menu. The role comes from /me once login is wired up (ticket 02). */
export default function Layout({ role }: { role?: Role }) {
  return (
    <div className="layout">
      <nav className="menu">
        <strong className="brand">Siam Bean</strong>
        {menuFor(role).map((item) => (
          <NavLink key={item.path} to={item.path}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
