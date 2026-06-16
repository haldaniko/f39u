import { apiClient, clearAuthTokens, storeAuthTokens } from "../api/client";

export async function loginAdmin(username, password) {
  clearAuthTokens();
  const { data } = await apiClient.post("/auth/login/", { username, password });
  storeAuthTokens(data);
  return fetchCurrentUser();
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get("/auth/me/");
  return data;
}

export function logoutAdmin() {
  clearAuthTokens();
}

export async function fetchAdminStatistics() {
  const { data } = await apiClient.get("/admin/statistics/");
  return data;
}

export async function fetchAdminArticles(params = {}) {
  const { data } = await apiClient.get("/admin/articles/", { params });
  return data;
}

export async function fetchAdminArticle(id) {
  const { data } = await apiClient.get(`/admin/articles/${id}/`);
  return data;
}

export async function fetchAdminOptions() {
  const { data } = await apiClient.get("/admin/options/");
  return data;
}

export async function createAdminArticle(payload) {
  const { data } = await apiClient.post("/admin/articles/", payload);
  return data;
}

export async function updateAdminArticle(id, payload) {
  const { data } = await apiClient.patch(`/admin/articles/${id}/`, payload);
  return data;
}

export async function deleteAdminArticle(id) {
  await apiClient.delete(`/admin/articles/${id}/`);
}
