const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const response = await fetchWithRetry(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = "No fue posible completar la solicitud.";
    try {
      const body = await response.json();
      message = normalizeApiError(body.detail, response.status, message);
    } catch {
      message = response.status >= 500
        ? "El servidor esta respondiendo lentamente. El sistema volvera a intentarlo."
        : response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function fetchWithRetry(url: string, options: RequestInit): Promise<Response> {
  const method = (options.method ?? "GET").toUpperCase();
  const retryable = method === "GET";
  const delays = [1200, 2800, 5000];

  for (let attempt = 0; attempt <= delays.length; attempt += 1) {
    try {
      const response = await fetch(url, options);
      const shouldRetry = retryable && response.status >= 500 && attempt < delays.length;
      if (!shouldRetry) return response;
    } catch {
      if (!retryable || attempt === delays.length) {
        throw new ApiError("El servidor esta iniciando o no responde. Espera unos segundos y vuelve a intentarlo.", 0);
      }
    }

    await wait(delays[attempt]);
  }

  throw new ApiError("La conexion con el servidor se interrumpio temporalmente. Se reintentara automaticamente.", 0);
}

function wait(milliseconds: number) {
  return new Promise<void>((resolve) => window.setTimeout(resolve, milliseconds));
}

export function buildAdminDownloadUrl(path: string, params: URLSearchParams): string {
  return `${API_BASE_URL}${path}?${params.toString()}`;
}

function normalizeApiError(detail: unknown, status: number, fallback: string) {
  if (status === 409) return "Usuario ya registrado.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) return String(item.msg);
        return String(item);
      })
      .join(" ");
  }
  return fallback;
}
