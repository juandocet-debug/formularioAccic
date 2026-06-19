import { useEffect, useState } from "react";
import type { Registration, RegistrationFilters, RegistrationPayload, TrainingGroup } from "../../../shared/domain/types";
import { deleteRegistration, downloadAdminFile, fetchCapacity, fetchRegistrations, updateRegistration } from "../infrastructure/adminApi";

export function useAdminPanel(token: string | null) {
  const [filters, setFilters] = useState<RegistrationFilters>({});
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [capacity, setCapacity] = useState<TrainingGroup[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load(nextFilters = filters) {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const [rows, capacityRows] = await Promise.all([fetchRegistrations(token, nextFilters), fetchCapacity(token)]);
      setRegistrations(rows.items);
      setTotal(rows.total);
      setCapacity(capacityRows);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "No fue posible cargar el panel.");
    } finally {
      setLoading(false);
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

  async function showGroup(groupId: number) {
    const nextFilters = { ...filters, group_id: String(groupId) };
    setFilters(nextFilters);
    await load(nextFilters);
  }

  useEffect(() => {
    void load();
  }, [token]);

  return { filters, setFilters, registrations, capacity, total, error, loading, load, save, remove, download, showGroup };
}
