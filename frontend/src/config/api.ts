/** Backend base URL — set VITE_API_BASE_URL in production (e.g. Render). */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function apiUrl(path: string): string {
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL.replace(/\/$/, "")}${suffix}`;
}
