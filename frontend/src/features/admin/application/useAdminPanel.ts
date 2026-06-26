import { useEffect, useMemo, useRef, useState } from "react";
import type { Registration, RegistrationFilters, RegistrationPayload, TrainingGroup } from "../../../shared/domain/types";
import { ApiError } from "../../../shared/infrastructure/apiClient";
import { deleteRegistration, downloadAdminFile, fetchCapacity, fetchRegistrations, importRegistrationsCsv, updateRegistration } from "../infrastructure/adminApi";

const PAGE_SIZE = 20;
const ADMIN_CACHE_LIMIT = 200;

export function useAdminPanel(token: string | null) {
  const [filters, setFilters] = useState<RegistrationFilters>({});
  const [allRegistrations, setAllRegistrations] = useState<Registration[]>([]);
  const [capacity, setCapacity] = useState<TrainingGroup[]>([]);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const retryTimer = useRef<number | null>(null);

  const filteredRegistrations = useMemo(
    () => allRegistrations.filter((registration) => matchesFilters(registration, filters, capacity)),
    [allRegistrations, filters, capacity],
  );
  const total = filteredRegistrations.length;
  const registrations = filteredRegistrations.slice(offset, offset + PAGE_SIZE);

  async function load(retryAttempt = 0) {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      // The response set is intentionally cached in the browser: filtering 200 rows is immediate.
      const rows = await fetchRegistrations(token, {}, ADMIN_CACHE_LIMIT, 0);
      setAllRegistrations(rows.items);
      setOffset(0);
      void refreshCapacity(token);
    } catch (requestError) {
      const isTransient = requestError instanceof ApiError && requestError.status === 0;
      setError(
        isTransient
          ? "Conexion temporalmente interrumpida. Intentando recuperar las respuestas..."
          : requestError instanceof Error
            ? requestError.message
            : "No fue posible cargar el panel.",
      );
      if (isTransient && retryAttempt < 3) {
        retryTimer.current = window.setTimeout(() => void load(retryAttempt + 1), 2500);
      }
    } finally {
      setLoading(false);
    }
  }

  async function refreshCapacity(activeToken: string) {
    try {
      setCapacity(await fetchCapacity(activeToken));
    } catch {
      // The table is still useful while the secondary capacity request recovers.
    }
  }

  async function save(registrationId: number, payload: RegistrationPayload) {
    if (!token) return;
    await updateRegistration(token, registrationId, payload);
    await load();
  }

  async function remove(registrationId: number) {
    if (!token) return;
    await deleteRegistration(token, registrationId);
    await load();
  }

  async function download(type: "excel" | "pdf") {
    if (!token) return;
    await downloadAdminFile(token, type === "excel" ? "/admin/exports/excel" : "/admin/exports/pdf", filters);
  }

  async function importCsv(file: File) {
    if (!token) return;
    setLoading(true);
    setError(null);
    setNotice(null);
    try {
      const result = await importRegistrationsCsv(token, file);
      const firstErrors = result.errors
        .slice(0, 3)
        .map((item) => `fila ${item.row ?? "-"}: ${item.message}`)
        .join(" | ");
      setNotice(
        result.rejected > 0
          ? `CSV procesado: ${result.imported} importadas y ${result.rejected} rechazadas. ${firstErrors}`
          : `CSV procesado: ${result.imported} registros importados correctamente.`,
      );
      await load();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "No fue posible importar el CSV.");
    } finally {
      setLoading(false);
    }
  }

  function showGroup(groupId: number) {
    setFilters((current) => ({ ...current, group_id: String(groupId) }));
    setOffset(0);
  }

  function applyFilters() {
    setOffset(0);
  }

  function nextPage() {
    if (offset + PAGE_SIZE < total) setOffset(offset + PAGE_SIZE);
  }

  function previousPage() {
    setOffset(Math.max(offset - PAGE_SIZE, 0));
  }

  useEffect(() => {
    void load();
    return () => {
      if (retryTimer.current !== null) window.clearTimeout(retryTimer.current);
    };
  }, [token]);

  return {
    filters,
    setFilters,
    registrations,
    capacity,
    total,
    offset,
    pageSize: PAGE_SIZE,
    error,
    notice,
    loading,
    load,
    save,
    remove,
    download,
    importCsv,
    showGroup,
    applyFilters,
    nextPage,
    previousPage,
  };
}

function matchesFilters(registration: Registration, filters: RegistrationFilters, capacity: TrainingGroup[]) {
  const name = `${registration.first_name} ${registration.second_name ?? ""} ${registration.first_last_name} ${registration.second_last_name ?? ""}`.toLowerCase();
  if (filters.name && !name.includes(filters.name.toLowerCase())) return false;
  if (filters.document && !registration.document_number.includes(filters.document)) return false;
  if (filters.place && !registration.place.toLowerCase().includes(filters.place.toLowerCase())) return false;
  if (filters.group_id && registration.group_id !== Number(filters.group_id)) return false;
  if (filters.date && registration.created_at.slice(0, 10) !== filters.date) return false;

  if (filters.capacity_status && capacity.length > 0) {
    const group = capacity.find((item) => item.group_id === registration.group_id);
    if (filters.capacity_status === "full" && !group?.is_full) return false;
    if (filters.capacity_status === "available" && group?.is_full) return false;
  }
  return true;
}
