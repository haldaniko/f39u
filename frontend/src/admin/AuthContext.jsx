import { createContext, useContext, useEffect, useState } from "react";

import { getStoredAccessToken } from "../api/client";
import { fetchCurrentUser, loginAdmin, logoutAdmin } from "../services/adminService";

const AuthContext = createContext(null);

export function AdminAuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(Boolean(getStoredAccessToken()));

  useEffect(() => {
    const expireSession = () => {
      logoutAdmin();
      setUser(null);
      setIsLoading(false);
    };
    window.addEventListener("fxlfm:auth-expired", expireSession);

    if (getStoredAccessToken()) {
      fetchCurrentUser()
        .then((currentUser) => {
          if (!currentUser.is_staff) throw new Error("Administrator access is required.");
          setUser(currentUser);
        })
        .catch(expireSession)
        .finally(() => setIsLoading(false));
    }

    return () => window.removeEventListener("fxlfm:auth-expired", expireSession);
  }, []);

  const login = async (username, password) => {
    const currentUser = await loginAdmin(username, password);
    setUser(currentUser);
    return currentUser;
  };

  const logout = () => {
    logoutAdmin();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAdminAuth() {
  return useContext(AuthContext);
}
