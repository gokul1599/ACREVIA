"use client";
// ACREVIA Offline Indicator & Synchronization Banner Component

import React, { useState, useEffect } from "react";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { OfflineQueue } from "@/lib/offline/queue";
import { useTranslation } from "@/lib/localization/context";
import { api } from "@/lib/api/client";
import { WifiOff, RefreshCw, CheckCircle2 } from "lucide-react";

export const OfflineBanner: React.FC = () => {
  const isOnline = useOnlineStatus();
  const { t } = useTranslation();
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [syncSuccess, setSyncSuccess] = useState<boolean>(false);

  const checkQueue = () => {
    const drafts = OfflineQueue.getDrafts();
    setPendingCount(drafts.length);
  };

  useEffect(() => {
    checkQueue();
    const interval = setInterval(checkQueue, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleSync = async () => {
    if (!isOnline || isSyncing) return;
    setIsSyncing(true);
    setSyncSuccess(false);
    try {
      const res = await OfflineQueue.syncAll(api);
      if (res.synced > 0) {
        setSyncSuccess(true);
        setTimeout(() => setSyncSuccess(false), 4000);
      }
      checkQueue();
    } finally {
      setIsSyncing(false);
    }
  };

  if (isOnline && pendingCount === 0 && !syncSuccess) {
    return null;
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className={`px-4 py-2.5 text-sm font-medium transition-colors ${
        !isOnline
          ? "bg-[#FEF3C7] text-[#92400E] border-b border-[#FCD34D]"
          : syncSuccess
          ? "bg-[#DCFCE7] text-[#166534] border-b border-[#86EFAC]"
          : "bg-[#DBEAFE] text-[#1E40AF] border-b border-[#93C5FD]"
      }`}
    >
      <div className="max-w-4xl mx-auto flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {!isOnline ? (
            <>
              <WifiOff className="w-4 h-4 shrink-0 text-[#D97706]" />
              <span>{t.common.offlineNotice}</span>
            </>
          ) : syncSuccess ? (
            <>
              <CheckCircle2 className="w-4 h-4 shrink-0 text-[#166534]" />
              <span>All offline drafts synchronized successfully to ACREVIA!</span>
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4 shrink-0 text-[#1E40AF]" />
              <span>
                {pendingCount} {t.common.syncPending}
              </span>
            </>
          )}
        </div>

        {isOnline && pendingCount > 0 && (
          <button
            type="button"
            onClick={handleSync}
            disabled={isSyncing}
            className="px-3 py-1 bg-white text-[#1E40AF] rounded-md font-semibold text-xs border border-[#93C5FD] hover:bg-[#EFF6FF] active:scale-95 disabled:opacity-50 touch-target"
          >
            {isSyncing ? "Syncing..." : t.common.syncNow}
          </button>
        )}
      </div>
    </div>
  );
};
