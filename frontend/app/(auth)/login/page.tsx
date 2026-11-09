"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";
import { useTranslation } from "@/lib/localization/context";
import { ApiError } from "@/lib/api/client";
import { Button } from "@/components/ui/Button";
import { Sprout, Phone, Lock, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const { t } = useTranslation();

  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;
    setError(null);

    if (!phone || !password) {
      setError("Please fill in both phone number and password.");
      return;
    }

    setIsLoading(true);
    try {
      await login({ phone: phone.trim(), password });
      router.push("/dashboard");
    } catch (err: unknown) {
      let msg = "Invalid credentials. Please verify your phone number and password.";
      if (err instanceof ApiError) {
        msg = err.message;
      } else if (err instanceof Error) {
        msg = err.message;
      }
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-card border border-[#E5E0D8] p-6 sm:p-8">
        <div className="text-center mb-6">
          <div className="w-14 h-14 bg-[#1E3A2B] rounded-2xl mx-auto flex items-center justify-center shadow-sm mb-3">
            <Sprout className="w-8 h-8 text-[#86EFAC]" />
          </div>
          <h1 className="text-2xl font-bold text-[#1E3A2B] tracking-tight">{t.auth.signIn}</h1>
          <p className="text-sm text-[#556059] mt-1">{t.app.subheading}</p>
        </div>

        {error && (
          <div
            role="alert"
            className="mb-4 p-3 bg-[#FFE3E3] border border-[#FFA8A8] text-[#C92A2A] rounded-xl text-sm flex items-start gap-2"
          >
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#1A241F] uppercase tracking-wider mb-1">
              {t.auth.phone}
            </label>
            <div className="relative">
              <Phone className="w-5 h-5 text-[#78857E] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder={t.auth.phonePlaceholder}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] focus:bg-white text-base focus:ring-2 focus:ring-[#1E3A2B] focus:border-transparent outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#1A241F] uppercase tracking-wider mb-1">
              {t.auth.password}
            </label>
            <div className="relative">
              <Lock className="w-5 h-5 text-[#78857E] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t.auth.passwordPlaceholder}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] focus:bg-white text-base focus:ring-2 focus:ring-[#1E3A2B] focus:border-transparent outline-none transition-all"
              />
            </div>
          </div>

          <Button type="submit" className="w-full" size="lg" isLoading={isLoading} disabled={isLoading}>
            {t.auth.loginSubmit}
          </Button>
        </form>

        <div className="mt-6 pt-6 border-t border-[#E5E0D8] text-center text-sm text-[#556059]">
          <span>{t.auth.noAccount} </span>
          <Link href="/register" className="font-semibold text-[#1E3A2B] hover:underline">
            {t.auth.register}
          </Link>
        </div>
      </div>
    </div>
  );
}
