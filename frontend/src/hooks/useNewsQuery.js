import { useInfiniteQuery, useQuery } from "@tanstack/react-query";

import { fetchArticle, fetchAuthor, fetchCategories, fetchNews, fetchTrending, searchNews } from "../services/newsService";

export function useInfiniteNews() {
  return useInfiniteQuery({
    queryKey: ["news", "infinite"],
    queryFn: ({ pageParam }) => fetchNews({ pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage, pages) => {
      if (!lastPage?.next) {
        return undefined;
      }
      return pages.length + 1;
    },
  });
}

export function useTrending() {
  return useQuery({ queryKey: ["trending"], queryFn: fetchTrending });
}

export function useCategories() {
  return useQuery({ queryKey: ["categories"], queryFn: fetchCategories });
}

export function useArticle(slug) {
  return useQuery({
    queryKey: ["article", slug],
    queryFn: () => fetchArticle(slug),
    enabled: Boolean(slug),
  });
}

export function useAuthor(slug) {
  return useQuery({
    queryKey: ["author", slug],
    queryFn: () => fetchAuthor(slug),
    enabled: Boolean(slug),
  });
}

export function useSearch(query) {
  return useQuery({
    queryKey: ["search", query],
    queryFn: () => searchNews(query),
    enabled: query.length > 1,
  });
}
