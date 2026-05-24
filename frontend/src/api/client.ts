const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

export const apiBaseUrl =
  configuredBaseUrl?.replace(/\/+$/, "") || "http://127.0.0.1:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`, {
      credentials: "include",
      headers: { Accept: "application/json" },
      signal,
    });
  } catch {
    throw new ApiError("Сервер данных недоступен. Проверьте, что он запущен.", 0);
  }

  if (!response.ok) {
    let detail = `Сервер данных вернул ошибку ${response.status}.`;

    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        detail = payload.detail;
      }
    } catch {
      // Keep the status-based fallback for non-JSON errors.
    }

    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

export async function apiPatch<T>(
  path: string,
  payload: Record<string, unknown>,
  signal?: AbortSignal,
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`, {
      body: JSON.stringify(payload),
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      method: "PATCH",
      signal,
    });
  } catch {
    throw new ApiError("Сервер данных недоступен. Проверьте, что он запущен.", 0);
  }

  if (!response.ok) {
    let detail = `Сервер данных вернул ошибку ${response.status}.`;

    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        detail = payload.detail;
      }
    } catch {
      // Keep the status-based fallback for non-JSON errors.
    }

    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}
