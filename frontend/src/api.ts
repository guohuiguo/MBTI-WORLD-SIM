import type { FrontendOverview, StateResponse } from "./types";

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, "") ||
  "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;

  try {
    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers ?? {}),
      },
      ...options,
    });

    if (!res.ok) {
      let detail = "";
      try {
        detail = await res.text();
      } catch {
        detail = "";
      }
      throw new Error(`Request failed: ${res.status} ${res.statusText}${detail ? ` - ${detail}` : ""}`);
    }

    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error(
        `Failed to fetch backend at ${url}. 请确认：1) 后端已启动 2) FastAPI 已开启 CORS 3) VITE_API_BASE_URL 正确。`
      );
    }
    throw err;
  }
}

export async function fetchOverview(): Promise<FrontendOverview> {
  return request<FrontendOverview>("/frontend/overview");
}

export async function fetchState(): Promise<StateResponse> {
  return request<StateResponse>("/state");
}

export async function resetSimulation(): Promise<{ ok: boolean; message: string }> {
  return request("/simulation/reset", { method: "POST" });
}

export async function stepSimulation(): Promise<unknown> {
  return request("/simulation/step", { method: "POST" });
}

export async function runDay(): Promise<unknown> {
  return request("/simulation/run-day", { method: "POST" });
}