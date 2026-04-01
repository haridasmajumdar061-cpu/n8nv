import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { useAuthStore } from "./hooks/useAuthStore";

export default function App() {
  const token = useAuthStore((s) => s.token);
  return token ? <DashboardPage /> : <LoginPage />;
}
