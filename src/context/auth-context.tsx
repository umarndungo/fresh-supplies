"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { fetchCurrentUserRequest, loginRequest, logoutRequest, registerRequest } from "@/lib/api/auth.api";
import { setAccessToken, clearAccessToken } from "@/lib/api/client";
import { SESSION_FLAG_COOKIE } from "@/lib/constants";
import { env } from "@/lib/env";
import type { AuthUser, LoginCredentials, RegisterPayload } from "@/types/auth.types";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

interface AuthContextValue {
  user: AuthUser | null;
  status: AuthStatus;
  login: (credentials: LoginCredentials) => Promise<AuthUser>;
  register: (payload: RegisterPayload) => Promise<AuthUser>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const DEMO_USER: AuthUser = {
  id: "dev-user-001",
  email: "dev@freshroute.ai",
  fullName: "Development User",
  role: "ADMINISTRATOR",
  organizationName: "FreshRoute AI Demo",
  avatarUrl: null,
  createdAt: new Date().toISOString(),
};

function setSessionFlag(present: boolean) {
  if (typeof document === "undefined") return;
  document.cookie = present
    ? `${SESSION_FLAG_COOKIE}=1; path=/; max-age=${60 * 60 * 24 * 7}; samesite=lax`
    : `${SESSION_FLAG_COOKIE}=; path=/; max-age=0; samesite=lax`;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<AuthStatus>("loading");

  const hydrate = useCallback(async () => {
    if (env.NEXT_PUBLIC_DEV_AUTH_BYPASS) {
      setUser(DEMO_USER);
      setStatus("authenticated");
      setSessionFlag(true);
      return;
    }

    try {
      const currentUser = await fetchCurrentUserRequest();
      setUser(currentUser);
      setStatus("authenticated");
      setSessionFlag(true);
    } catch {
      setUser(null);
      setStatus("unauthenticated");
      setSessionFlag(false);
    }
  }, []);

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (env.NEXT_PUBLIC_DEV_AUTH_BYPASS) return;

    function handleExpiry() {
      clearAccessToken();
      setUser(null);
      setStatus("unauthenticated");
      setSessionFlag(false);
    }
    window.addEventListener("freshroute:session-expired", handleExpiry);
    return () => window.removeEventListener("freshroute:session-expired", handleExpiry);
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    if (env.NEXT_PUBLIC_DEV_AUTH_BYPASS) {
      setUser(DEMO_USER);
      setStatus("authenticated");
      setSessionFlag(true);
      return DEMO_USER;
    }

    const result = await loginRequest(credentials);
    setAccessToken(result.accessToken);
    setUser(result.user);
    setStatus("authenticated");
    setSessionFlag(true);
    return result.user;
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    if (env.NEXT_PUBLIC_DEV_AUTH_BYPASS) {
      setUser(DEMO_USER);
      setStatus("authenticated");
      setSessionFlag(true);
      return DEMO_USER;
    }

    const result = await registerRequest(payload);
    setAccessToken(result.accessToken);
    setUser(result.user);
    setStatus("authenticated");
    setSessionFlag(true);
    return result.user;
  }, []);

  const logout = useCallback(async () => {
    if (env.NEXT_PUBLIC_DEV_AUTH_BYPASS) {
      setUser(DEMO_USER);
      setStatus("authenticated");
      setSessionFlag(true);
      return;
    }

    try {
      await logoutRequest();
    } finally {
      clearAccessToken();
      setUser(null);
      setStatus("unauthenticated");
      setSessionFlag(false);
    }
  }, []);

  const value = useMemo(
    () => ({ user, status, login, register, logout }),
    [user, status, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used within an AuthProvider");
  return ctx;
}
