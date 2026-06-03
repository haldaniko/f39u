import { apiClient } from "../api/client";

export async function fetchNews({ pageParam = 1 }) {
  const { data } = await apiClient.get("/news/", { params: { page: pageParam } });
  if (Array.isArray(data)) {
    return { results: data, next: null };
  }
  return data;
}

export async function fetchArticle(slug) {
  const { data } = await apiClient.get(`/news/${slug}/`);
  return data;
}

export async function fetchTrending() {
  const { data } = await apiClient.get("/trending/");
  return data;
}

export async function fetchCategories() {
  const { data } = await apiClient.get("/categories/");
  if (Array.isArray(data)) {
    return data;
  }
  return data?.results || [];
}

export async function searchNews(q) {
  const { data } = await apiClient.get("/search/", { params: { q } });
  return data;
}
