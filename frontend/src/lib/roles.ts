export type Role = "admin" | "sales" | "warehouse" | "accountant";

const ALL: Role[] = ["admin", "sales", "warehouse", "accountant"];

export type MenuItem = { label: string; path: string; roles: Role[] };

// Role matrix from docs/plan.md. Hiding a link is not security: the API checks too.
export const MENU: MenuItem[] = [
  { label: "Dashboard", path: "/dashboard", roles: ALL },
  { label: "Products", path: "/products", roles: ALL },
  { label: "Customers", path: "/customers", roles: ["admin", "sales", "accountant"] },
  { label: "Stock in", path: "/stock-in", roles: ["admin", "warehouse"] },
  { label: "Sales orders", path: "/orders", roles: ["admin", "sales"] },
  { label: "Invoices", path: "/invoices", roles: ["admin", "sales", "accountant"] },
  { label: "Accounting", path: "/accounting", roles: ["admin", "accountant"] },
  { label: "Purchase orders", path: "/purchase-orders", roles: ["admin", "warehouse"] },
];

/** Menu items for a role. With no role yet (before login is wired up), all items. */
export function menuFor(role: Role | undefined): MenuItem[] {
  return role ? MENU.filter((item) => item.roles.includes(role)) : MENU;
}
