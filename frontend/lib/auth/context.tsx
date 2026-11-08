"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { UserSummary } from "@/lib/api/types";
import { api } from "@/lib/api/client";

interface AuthContextType {
  user: UserSummary | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: { phone?: string; email?: string; password: string }) => Promise<void>;
  register: (data: {
    phone: string;
    full_name: string;
    password: string;
    email?: string;
    language_preference?: string;
    role?: string;
  }) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    try {
      const token = api.getToken();
      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }
      const profile = await api.getCurrentUser();
      setUser(profile);
    } catch {
      setUser(null);
      api.setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (credentials: { phone?: string; email?: string; password: string }) => {
    setIsLoading(true);
    try {
      const res = await api.login(credentials);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: {
    phone: string;
    full_name: string;
    password: string;
    email?: string;
    language_preference?: string;
    role?: string;
  }) => {
    setIsLoading(true);
    try {
      await api.register(data);
      // Automatically log in after registration
      const loginRes = await api.login({
        phone: data.phone,
        password: data.password,
      });
      setUser(loginRes.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.setToken(null);
    setUser(null);
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
