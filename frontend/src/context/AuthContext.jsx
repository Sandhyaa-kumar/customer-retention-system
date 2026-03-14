import { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
  apiFetch,
  clearToken,
  getToken,
  loginRequest,
  setToken,
} from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, validate any persisted token against the /me endpoint.
  useEffect(() => {
    const bootstrap = async () => {
      const token = getToken();
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const me = await apiFetch("/api/auth/me");
        setUser(me.user);
      } catch {
        // Token invalid or expired — clear it silently.
        clearToken();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    bootstrap();
  }, []);

  const login = async (username, password) => {
    const result = await loginRequest(username, password);
    setToken(result.token);
    setUser(result.user);
    return result.user;
  };

  const logout = () => {
    clearToken();
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, loading, isAuthenticated: Boolean(user), login, logout }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be called inside AuthProvider");
  }
  return context;
}
