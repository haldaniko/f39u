import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const ACCESS_TOKEN_KEY = "fxlfm_admin_access";
const REFRESH_TOKEN_KEY = "fxlfm_admin_refresh";

export function getStoredAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function storeAuthTokens({ access, refresh }) {
  if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function clearAuthTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  const token = getStoredAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshRequest = null;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    const isAuthRequest = originalRequest?.url?.includes("/auth/");

    if (error.response?.status === 401 && refreshToken && !originalRequest?._retry && !isAuthRequest) {
      originalRequest._retry = true;
      try {
        refreshRequest ||= axios.post(`${API_BASE_URL}/auth/refresh/`, { refresh: refreshToken });
        const { data } = await refreshRequest;
        storeAuthTokens(data);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return apiClient(originalRequest);
      } catch {
        clearAuthTokens();
        window.dispatchEvent(new Event("fxlfm:auth-expired"));
      } finally {
        refreshRequest = null;
      }
    }

    const payload = error.response?.data;
    const fieldMessage = payload && typeof payload === "object"
      ? Object.values(payload).flat().find(Boolean)
      : null;
    const message = payload?.detail || fieldMessage || error.message || "Request failed";
    return Promise.reject(new Error(String(message)));
  }
);
