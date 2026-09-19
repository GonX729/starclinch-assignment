import api from "./api";

export async function login(username: string, password: string) {
  const res = await api.post("/auth/login/", { username, password });
  localStorage.setItem("access_token", res.data.access);
  localStorage.setItem("refresh_token", res.data.refresh);
  return res.data;
}

export async function logout() {
  try {
    const refresh = localStorage.getItem("refresh_token");
    await api.post("/auth/logout/", { refresh });
  } catch {
    // proceed even if the backend call fails
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
  }
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
}
