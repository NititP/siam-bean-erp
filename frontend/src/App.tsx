import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
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

// Every page's route lives here (Part 3). Owners edit only their page files.
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        {/* Part 1 */}
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/customers" element={<CustomersPage />} />
        <Route path="/stock-in" element={<StockInPage />} />
        <Route path="/purchase-orders" element={<PurchaseOrdersPage />} />
        {/* Part 2 */}
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/orders/new" element={<NewOrderPage />} />
        <Route path="/orders/:id" element={<OrderDetailPage />} />
        <Route path="/invoices" element={<InvoicesPage />} />
        <Route path="/invoices/:id" element={<InvoiceDetailPage />} />
        {/* Part 3 */}
        <Route path="/accounting" element={<AccountingPage />} />
        <Route path="/access-denied" element={<AccessDeniedPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
