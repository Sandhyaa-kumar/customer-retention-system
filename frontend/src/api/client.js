const RAW_API_BASE = import.meta.env.VITE_API_URL || "";
const API_BASE = RAW_API_BASE.endsWith("/") ? RAW_API_BASE.slice(0, -1) : RAW_API_BASE;

function buildApiUrl(path) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalizedPath}`;
}

export function getToken() {
  return sessionStorage.getItem("auth_token") || "";
}

export function setToken(token) {
  sessionStorage.setItem("auth_token", token);
  // Remove any older persistent token so close-tab means logout.
  localStorage.removeItem("auth_token");
}

export function clearToken() {
  sessionStorage.removeItem("auth_token");
  localStorage.removeItem("auth_token");
}

/**
 * Base API fetch that automatically injects the JWT Authorization header.
 * Throws an Error (with a .status property) on non-2xx responses.
 */
export async function apiFetch(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(buildApiUrl(path), {
    ...options,
    headers,
  });

  let payload = null;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    payload = await response.json();
  }

  if (!response.ok) {
    const message = payload?.error || `Request failed with status ${response.status}`;
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return payload;
}

export async function loginRequest(username, password) {
  return apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}
