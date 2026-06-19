import { apiRequest, buildAdminDownloadUrl } from "../../../shared/infrastructure/apiClient";
import type { Registration, RegistrationFilters, RegistrationPayload, TrainingGroup } from "../../../shared/domain/types";

type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_minutes: number;
};

type RegistrationListResponse = {
  items: Registration[];
  total: number;
  limit: number;
  offset: number;
};

function paramsFromFilters(filters: RegistrationFilters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  return params;
}

export function login(username: string, password: string) {
  return apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function fetchRegistrations(token: string, filters: RegistrationFilters, limit = 50, offset = 0) {
  const params = paramsFromFilters(filters);
  params.set("limit", String(limit));
  params.set("offset", String(offset));
  return apiRequest<RegistrationListResponse>(`/admin/registrations?${params.toString()}`, {}, token);
}

export function fetchCapacity(token: string) {
  return apiRequest<TrainingGroup[]>("/admin/capacity", {}, token);
}

export function updateRegistration(token: string, registrationId: number, payload: RegistrationPayload) {
  return apiRequest<Registration>(`/admin/registrations/${registrationId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  }, token);
}

export function deleteRegistration(token: string, registrationId: number) {
  return apiRequest<void>(`/admin/registrations/${registrationId}`, { method: "DELETE" }, token);
}

export async function downloadAdminFile(token: string, path: "/admin/exports/excel" | "/admin/exports/pdf", filters: RegistrationFilters) {
  const response = await fetch(buildAdminDownloadUrl(path, paramsFromFilters(filters)), {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("No fue posible descargar el archivo.");
  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = disposition.match(/filename="([^"]+)"/);
  const filename = match?.[1] ?? (path.endsWith("pdf") ? "respuestas.pdf" : "respuestas.xlsx");
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
