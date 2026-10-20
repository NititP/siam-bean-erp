import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Allow from "./components/Allow";
import Layout from "./components/Layout";
import RequireLogin from "./components/RequireLogin";
import { PAGE_ROLES, type Role } from "./lib/roles";
import AccessDeniedPage from "./pages/AccessDeniedPage";
import AccountingPage from "./pages/AccountingPage";
import CustomersPage from "./pages/CustomersPage";
import DashboardPage from "./pages/DashboardPage";
import InvoiceDetailPage from "./pages/InvoiceDetailPage";
import InvoicesPage from "./pages/InvoicesPage";
import LoginPage from "./pages/LoginPage";
import NewOrderPage from "./pages/NewOrderPage";
import OrderDetailPage from "./pages/OrderDetailPage";
import OrdersPage from "./pages/OrdersPage";
import ProductsPage from "./pages/ProductsPage";
import PurchaseOrdersPage from "./pages/PurchaseOrdersPage";
import StockInPage from "./pages/StockInPage";

const only = (roles: Role[], page: ReactNode) => <Allow roles={roles}>{page}</Allow>;

// Every page's route lives here (Part 3). Owners edit only their page files.
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireLogin>
            <Layout />
          </RequireLogin>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        {/* Part 1 */}
        <Route path="/dashboard" element={only(PAGE_ROLES.dashboard, <DashboardPage />)} />
        <Route path="/products" element={only(PAGE_ROLES.products, <ProductsPage />)} />
        <Route path="/customers" element={only(PAGE_ROLES.customers, <CustomersPage />)} />
        <Route path="/stock-in" element={only(PAGE_ROLES.stockIn, <StockInPage />)} />
        <Route path="/purchase-orders" element={only(PAGE_ROLES.purchaseOrders, <PurchaseOrdersPage />)} />
        {/* Part 2 */}
        <Route path="/orders" element={only(PAGE_ROLES.orders, <OrdersPage />)} />
        <Route path="/orders/new" element={only(PAGE_ROLES.orders, <NewOrderPage />)} />
        <Route path="/orders/:id" element={only(PAGE_ROLES.orders, <OrderDetailPage />)} />
        <Route path="/invoices" element={only(PAGE_ROLES.invoices, <InvoicesPage />)} />
        <Route path="/invoices/:id" element={only(PAGE_ROLES.invoices, <InvoiceDetailPage />)} />
        {/* Part 3 */}
        <Route path="/accounting" element={only(PAGE_ROLES.accounting, <AccountingPage />)} />
        <Route path="/access-denied" element={<AccessDeniedPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
