import { apiClient } from "../api/client";

export async function subscribeToNewsletter(email, source) {
  const { data } = await apiClient.post("/newsletter/subscribe/", { email, source });
  return data;
}
