import { Download, LogOut, Pencil, RefreshCw, Save, Search, Trash2, Upload } from "lucide-react";
import { ChangeEvent, FormEvent, useRef, useState } from "react";
import { AVAILABLE_COURSES } from "../../../shared/domain/courses";
import type { Registration, RegistrationPayload } from "../../../shared/domain/types";
import { useAdminPanel } from "../application/useAdminPanel";

const ADMIN_GROUP_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

type Session = {
  token: string | null;
  error: string | null;
  signIn: (username: string, password: string) => Promise<boolean>;
  signOut: () => void;
};

export function AdminPanel({ session }: { session: Session }) {
  if (!session.token) return <LoginPanel session={session} />;
  return <Dashboard token={session.token} onSignOut={session.signOut} />;
}

function LoginPanel({ session }: { session: Session }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await session.signIn(username, password);
  }

  return (
    <section className="login-panel">
      <form className="form-surface compact" onSubmit={onSubmit}>
        <h2>Panel interno</h2>
        <label className="field">
          <span>Usuario</span>
          <input value={username} onChange={(event) => setUsername(event.target.value)} required />
        </label>
        <label className="field">
          <span>Contrasena</span>
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        {session.error && <p className="error">{session.error}</p>}
        <button className="primary-button" type="submit">Entrar</button>
      </form>
    </section>
  );
}

function Dashboard({ token, onSignOut }: { token: string; onSignOut: () => void }) {
  const panel = useAdminPanel(token);
  const csvInputRef = useRef<HTMLInputElement | null>(null);

  async function onCsvSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    await panel.importCsv(file);
  }

  return (
    <section className="admin-layout">
      <div className="admin-actions">
        <button className="ghost-button" onClick={() => panel.load()} title="Actualizar"><RefreshCw size={17} />Actualizar</button>
        <button className="ghost-button" onClick={() => csvInputRef.current?.click()} title="Importar registros desde CSV"><Upload size={17} />Importar CSV</button>
        <input ref={csvInputRef} className="hidden-file-input" type="file" accept=".csv,text/csv" onChange={onCsvSelected} />
        <button className="ghost-button" onClick={() => panel.download("excel")} title="Descargar Excel"><Download size={17} />Excel</button>
        <button className="ghost-button" onClick={() => panel.download("pdf")} title="Descargar PDF"><Download size={17} />PDF</button>
        <button className="ghost-button" onClick={onSignOut} title="Cerrar sesion"><LogOut size={17} />Salir</button>
      </div>

      <div className="capacity-grid">
        {panel.capacity.map((group) => (
          <button
            className={group.is_full ? "capacity-card full" : "capacity-card"}
            key={group.group_id}
            onClick={() => panel.showGroup(group.group_id)}
            title={`Ver inscritos del ${group.group_name}`}
            type="button"
          >
            <strong>{group.group_name}</strong>
            <span>{group.place}</span>
            <b>{group.registered_count}/{group.capacity}</b>
          </button>
        ))}
      </div>

      <div className="filters">
        <Search size={18} />
        <input placeholder="Nombre" value={panel.filters.name ?? ""} onChange={(e) => panel.setFilters({ ...panel.filters, name: e.target.value })} />
        <input placeholder="Documento" value={panel.filters.document ?? ""} onChange={(e) => panel.setFilters({ ...panel.filters, document: e.target.value })} />
        <input placeholder="Lugar" value={panel.filters.place ?? ""} onChange={(e) => panel.setFilters({ ...panel.filters, place: e.target.value })} />
        <input type="date" value={panel.filters.date ?? ""} onChange={(e) => panel.setFilters({ ...panel.filters, date: e.target.value })} />
        <select value={panel.filters.group_id ?? ""} onChange={(e) => panel.setFilters({ ...panel.filters, group_id: e.target.value })}>
          <option value="">Todos los grupos</option>
          {ADMIN_GROUP_IDS.map((groupId) => <option key={groupId} value={groupId}>Grupo {groupId}</option>)}
        </select>
        <select value={panel.filters.capacity_status ?? ""} onChange={(e) => panel.setFilters({ ...panel.filters, capacity_status: e.target.value })}>
          <option value="">Todos los cupos</option>
          <option value="available">Con cupo</option>
          <option value="full">Sin cupo</option>
        </select>
        <button className="primary-button small" onClick={panel.applyFilters}>Filtrar</button>
      </div>

      {panel.error && <p className="error">{panel.error}</p>}
      {panel.notice && <p className="success">{panel.notice}</p>}
      <p className="muted">
        {panel.loading
          ? "Cargando respuestas..."
          : panel.filters.group_id
            ? `${panel.total} inscritos en Grupo ${panel.filters.group_id}`
            : `${panel.total} respuestas registradas`}
      </p>
      <RegistrationTable rows={panel.registrations} onSave={panel.save} onDelete={panel.remove} />
      <div className="pagination-bar">
        <span>
          {panel.total === 0
            ? "Sin registros"
            : `Mostrando ${panel.offset + 1}-${Math.min(panel.offset + panel.registrations.length, panel.total)} de ${panel.total}`}
        </span>
        <div>
          <button className="ghost-button small" type="button" onClick={panel.previousPage} disabled={panel.offset === 0}>
            Anterior
          </button>
          <button
            className="ghost-button small"
            type="button"
            onClick={panel.nextPage}
            disabled={panel.offset + panel.pageSize >= panel.total}
          >
            Siguiente
          </button>
        </div>
      </div>
    </section>
  );
}

function RegistrationTable({
  rows,
  onSave,
  onDelete,
}: {
  rows: Registration[];
  onSave: (id: number, payload: RegistrationPayload) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [draft, setDraft] = useState<RegistrationPayload | null>(null);

  function startEdit(row: Registration) {
    setEditingId(row.id);
    setDraft({
      first_name: row.first_name,
      second_name: row.second_name ?? "",
      first_last_name: row.first_last_name,
      second_last_name: row.second_last_name ?? "",
      document_number: row.document_number,
      phone: row.phone,
      group_id: row.group_id,
      interested_courses: row.interested_courses ?? [],
    });
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Documento</th>
            <th>Nombre</th>
            <th>Telefono</th>
            <th>Cursos</th>
            <th>Grupo</th>
            <th>Lugar</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 && (
            <tr>
              <td colSpan={8} className="empty-cell">No hay inscritos para los filtros seleccionados.</td>
            </tr>
          )}
          {rows.map((row) => {
            const activeDraft = editingId === row.id ? draft : null;
            return (
              <tr key={row.id}>
                <td>{activeDraft ? <input value={activeDraft.document_number} inputMode="numeric" onChange={(e) => setDraft({ ...activeDraft, document_number: cleanNumber(e.target.value) })} /> : row.document_number}</td>
                <td>
                  {activeDraft ? (
                    <div className="inline-grid">
                      <input value={activeDraft.first_name} onChange={(e) => setDraft({ ...activeDraft, first_name: cleanText(e.target.value) })} />
                      <input value={activeDraft.second_name ?? ""} onChange={(e) => setDraft({ ...activeDraft, second_name: cleanText(e.target.value) })} />
                      <input value={activeDraft.first_last_name} onChange={(e) => setDraft({ ...activeDraft, first_last_name: cleanText(e.target.value) })} />
                      <input value={activeDraft.second_last_name ?? ""} onChange={(e) => setDraft({ ...activeDraft, second_last_name: cleanText(e.target.value) })} />
                    </div>
                  ) : (
                    `${row.first_name} ${row.second_name ?? ""} ${row.first_last_name} ${row.second_last_name ?? ""}`
                  )}
                </td>
                <td>{activeDraft ? <input value={activeDraft.phone} inputMode="numeric" onChange={(e) => setDraft({ ...activeDraft, phone: cleanNumber(e.target.value) })} /> : row.phone}</td>
                <td>
                  {activeDraft ? (
                    <div className="table-checks">
                      {AVAILABLE_COURSES.map((course) => {
                        const checked = activeDraft.interested_courses.includes(course);
                        return (
                          <label key={course}>
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={() =>
                                setDraft({
                                  ...activeDraft,
                                  interested_courses: checked
                                    ? activeDraft.interested_courses.filter((item) => item !== course)
                                    : [...activeDraft.interested_courses, course],
                                })
                              }
                            />
                            <span>{course}</span>
                          </label>
                        );
                      })}
                    </div>
                  ) : (
                    <span className="course-list">{(row.interested_courses ?? []).join(", ")}</span>
                  )}
                </td>
                <td>
                  {activeDraft ? (
                    <select value={activeDraft.group_id} onChange={(e) => setDraft({ ...activeDraft, group_id: Number(e.target.value) })}>
                      {ADMIN_GROUP_IDS.map((groupId) => <option key={groupId} value={groupId}>Grupo {groupId}</option>)}
                    </select>
                  ) : (
                    row.group_name
                  )}
                </td>
                <td>{row.place}</td>
                <td>{new Date(row.created_at).toLocaleString("es-CO")}</td>
                <td className="row-actions">
                  {activeDraft ? (
                    <button className="icon-button" title="Guardar" onClick={() => onSave(row.id, activeDraft).then(() => setEditingId(null))}><Save size={16} /></button>
                  ) : (
                    <button className="icon-button" title="Editar" onClick={() => startEdit(row)}><Pencil size={16} /></button>
                  )}
                  <button className="icon-button danger" title="Eliminar" onClick={() => window.confirm("Confirmar eliminacion") && onDelete(row.id)}><Trash2 size={16} /></button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function cleanText(value: string) {
  return value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñÜü ]/g, "");
}

function cleanNumber(value: string) {
  return value.replace(/\D/g, "");
}
