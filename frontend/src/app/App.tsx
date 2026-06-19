import { ShieldCheck } from "lucide-react";
import { AdminPanel } from "../features/admin/presentation/AdminPanel";
import { PublicRegistrationForm } from "../features/public-registration/presentation/PublicRegistrationForm";
import { useSession } from "../features/admin/application/useSession";

export function App() {
  const isAdminRoute = window.location.pathname.startsWith("/admin");
  const session = useSession();

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">Componente 5</span>
          <h1>Selección de Grupo de Capacitación – Escuela Popular de Artes y Oficios</h1>
        </div>
        <a className="admin-link" href={isAdminRoute ? "/" : "/admin"} title={isAdminRoute ? "Formulario publico" : "Panel interno"}>
          <ShieldCheck size={18} />
          <span>{isAdminRoute ? "Formulario" : "Admin"}</span>
        </a>
      </header>

      {isAdminRoute ? <AdminPanel session={session} /> : <PublicRegistrationForm />}
    </main>
  );
}
