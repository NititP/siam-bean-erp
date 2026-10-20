export type Role = "admin" | "sales" | "warehouse" | "accountant";

const ALL: Role[] = ["admin", "sales", "warehouse", "accountant"];

// Who may open each area: the role matrix in docs/plan.md. Hiding a page is
// not security: the API checks every request too.
export const PAGE_ROLES = {
  dashboard: ALL,
  products: ALL,
  customers: ["admin", "sales", "accountant"],
  stockIn: ["admin", "warehouse"],
  orders: ["admin", "sales"],
  invoices: ["admin", "sales", "accountant"],
  accounting: ["admin", "accountant"],
  purchaseOrders: ["admin", "warehouse"],
} satisfies Record<string, Role[]>;

export type MenuItem = { label: string; path: string; roles: Role[] };

export const MENU: MenuItem[] = [
  { label: "Dashboard", path: "/dashboard", roles: PAGE_ROLES.dashboard },
  { label: "Products", path: "/products", roles: PAGE_ROLES.products },
  { label: "Customers", path: "/customers", roles: PAGE_ROLES.customers },
  { label: "Stock in", path: "/stock-in", roles: PAGE_ROLES.stockIn },
  { label: "Sales orders", path: "/orders", roles: PAGE_ROLES.orders },
  { label: "Invoices", path: "/invoices", roles: PAGE_ROLES.invoices },
  { label: "Accounting", path: "/accounting", roles: PAGE_ROLES.accounting },
  { label: "Purchase orders", path: "/purchase-orders", roles: PAGE_ROLES.purchaseOrders },
];

/** The menu items a role may use. */
export function menuFor(role: Role): MenuItem[] {
  return MENU.filter((item) => item.roles.includes(role));
}
