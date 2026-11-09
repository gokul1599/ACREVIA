"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth/context";
import { useTranslation } from "@/lib/localization/context";
import { OfflineQueue, OfflineDraft } from "@/lib/offline/queue";
import { api } from "@/lib/api/client";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { LanguageSelector } from "@/components/ui/LanguageSelector";
import { Button } from "@/components/ui/Button";
import {
  User,
  Phone,
  Wifi,
  WifiOff,
  RefreshCw,
  LogOut,
  ShieldCheck,
  Trash2,
} from "lucide-react";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const isOnline = useOnlineStatus();

  const [drafts, setDrafts] = useState<OfflineDraft[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);

  const loadDrafts = () => {
    setDrafts(OfflineQueue.getDrafts());
  };

  useEffect(() => {
    loadDrafts();
  }, []);

  const handleManualSync = async () => {
    if (!isOnline || isSyncing) return;
    setIsSyncing(true);
    try {
      await OfflineQueue.syncAll(api);
      loadDrafts();
    } finally {
      setIsSyncing(false);
    }
  };

  const handleClearDrafts = () => {
    if (confirm("Are you sure you want to clear unsynchronized local drafts?")) {
      localStorage.removeItem("acrevia_offline_drafts_v1");
      loadDrafts();
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-[#1E3A2B] tracking-tight">{t.nav.profile}</h1>
        <p className="text-xs text-[#556059]">Farmer Account, Multilingual Preferences & Offline Synchronization</p>
      </div>

      {/* User Information Card */}
      <div className="bg-white rounded-2xl border border-[#E5E0D8] p-6 shadow-card space-y-4">
        <div className="flex items-center gap-4 border-b border-[#E5E0D8] pb-4">
          <div className="w-16 h-16 rounded-full bg-[#1E3A2B] text-white flex items-center justify-center text-xl font-bold">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : <User className="w-8 h-8" />}
          </div>
          <div>
            <h2 className="text-xl font-bold text-[#1A241F]">{user?.full_name || "ACREVIA Farmer"}</h2>
            <div className="flex items-center gap-2 text-xs text-[#556059] mt-0.5">
              <Phone className="w-3.5 h-3.5" />
              <span>{user?.phone || "No phone registered"}</span>
            </div>
            <div className="flex items-center gap-1 text-[11px] font-semibold text-[#15803D] mt-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Verified Telangana Farmer Account</span>
            </div>
          </div>
        </div>

        {/* Language Selection */}
        <div>
          <label className="block text-xs font-semibold text-[#1A241F] uppercase tracking-wider mb-2">
            {t.auth.selectLanguage}
          </label>
          <LanguageSelector />
        </div>
      </div>

      {/* Offline Storage & Queue Management */}
      <div className="bg-white rounded-2xl border border-[#E5E0D8] p-6 shadow-card space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isOnline ? (
              <Wifi className="w-5 h-5 text-[#15803D]" />
            ) : (
              <WifiOff className="w-5 h-5 text-[#D97706]" />
            )}
            <h3 className="font-bold text-base text-[#1E3A2B]">Offline Data Queue</h3>
          </div>
          <span
            className={`text-xs font-bold px-2.5 py-1 rounded-full ${
              isOnline ? "bg-[#DCFCE7] text-[#15803D]" : "bg-[#FEF3C7] text-[#D97706]"
            }`}
          >
            {isOnline ? "Online Connected" : "Offline Mode"}
          </span>
        </div>

        <p className="text-xs text-[#556059] leading-relaxed">
          ACREVIA saves your observations and crop photos locally if cell reception drops in the fields.
        </p>

        {drafts.length === 0 ? (
          <div className="p-4 bg-[#FAFAF7] rounded-xl text-xs text-[#78857E] text-center border border-[#E5E0D8]">
            Zero pending drafts. All local data is fully synchronized with ACREVIA backend servers.
          </div>
        ) : (
          <div className="space-y-2">
            <span className="text-xs font-semibold text-[#1A241F] block">
              {drafts.length} Unsynchronized Draft(s):
            </span>
            {drafts.map((d) => (
              <div
                key={d.id}
                className="p-3 bg-[#FAFAF7] rounded-xl border border-[#E5E0D8] flex items-center justify-between text-xs"
              >
                <div>
                  <span className="font-bold text-[#1A241F] block">{d.type}</span>
                  <span className="text-[11px] text-[#78857E]">
                    {new Date(d.created_at).toLocaleTimeString()} • {d.sync_status}
                  </span>
                </div>
                <span className="text-[11px] font-semibold text-[#D97706] uppercase">
                  Pending
                </span>
              </div>
            ))}

            <div className="flex gap-2 pt-2">
              <Button
                type="button"
                variant="primary"
                size="sm"
                onClick={handleManualSync}
                isLoading={isSyncing}
                disabled={!isOnline}
                icon={<RefreshCw className="w-4 h-4" />}
              >
                Sync Now
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleClearDrafts}
                icon={<Trash2 className="w-4 h-4 text-[#C92A2A]" />}
              >
                Clear Queue
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Sign Out */}
      <div className="pt-2">
        <Button
          type="button"
          variant="danger"
          size="lg"
          className="w-full"
          onClick={logout}
          icon={<LogOut className="w-5 h-5" />}
        >
          {t.auth.signOut}
        </Button>
      </div>
    </div>
  );
}
