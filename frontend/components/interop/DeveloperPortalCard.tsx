"use client";

import React, { useState } from "react";
import type { ApiApplication, ApiCredential } from "../../lib/api/types";

interface DeveloperPortalCardProps {
  applications: ApiApplication[];
  credentials: ApiCredential[];
  labels: {
    title: string;
    subtitle: string;
    applications: string;
    createApp: string;
    generateKey: string;
    rateLimit: string;
    secretWarning: string;
  };
  onCreateApp?: (name: string, isSandbox: boolean) => void;
  onGenerateKey?: (appId: string) => void;
  onRevokeKey?: (credId: string) => void;
  newSecret?: string | null;
}

export const DeveloperPortalCard: React.FC<DeveloperPortalCardProps> = ({
  applications,
  credentials,
  labels,
  onCreateApp,
  onGenerateKey,
  onRevokeKey,
  newSecret,
}) => {
  const [appName, setAppName] = useState("");
  const [isSandbox, setIsSandbox] = useState(true);
  const [selectedAppId, setSelectedAppId] = useState<string>(applications[0]?.id || "");

  return (
    <div className="bg-white rounded-xl shadow-sm border border-sky-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">{labels.subtitle}</p>
        </div>
      </div>

      {newSecret && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs space-y-1">
          <div className="flex items-center text-amber-800 font-semibold">
            <span className="mr-1.5">⚠️</span> {labels.secretWarning}
          </div>
          <div className="font-mono text-[11px] bg-white p-2 rounded border border-amber-200 text-gray-900 break-all select-all">
            {newSecret}
          </div>
        </div>
      )}

      {/* Create Application Section */}
      <div className="p-3 rounded-lg bg-sky-50/50 border border-sky-100 space-y-2">
        <h4 className="text-xs font-semibold text-gray-800">{labels.createApp}</h4>
        <div className="flex gap-2">
          <input
            type="text"
            value={appName}
            onChange={(e) => setAppName(e.target.value)}
            placeholder="Application Name (e.g. AgriSense IoT Integration)"
            className="flex-1 text-xs p-2 border border-gray-200 rounded bg-white focus:ring-1 focus:ring-sky-500"
          />
          <label className="inline-flex items-center text-xs text-gray-600 px-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isSandbox}
              onChange={(e) => setIsSandbox(e.target.checked)}
              className="rounded mr-1.5 text-sky-600"
            />
            Sandbox
          </label>
          <button
            onClick={() => {
              if (appName.trim() && onCreateApp) {
                onCreateApp(appName.trim(), isSandbox);
                setAppName("");
              }
            }}
            disabled={!appName.trim()}
            className="px-3 py-1.5 bg-sky-600 hover:bg-sky-700 disabled:opacity-50 text-white rounded text-xs font-medium"
          >
            Create
          </button>
        </div>
      </div>

      {/* Applications and Credentials List */}
      <div className="space-y-3">
        {applications.length === 0 ? (
          <div className="text-xs text-gray-400 py-4 text-center">No developer applications registered yet.</div>
        ) : (
          applications.map((app) => {
            const appCreds = credentials.filter((c) => c.application_id === app.id);

            return (
              <div key={app.id} className="p-3.5 rounded-lg border border-gray-100 bg-gray-50/40 space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-gray-900">{app.name}</span>
                    <span
                      className={`text-[9px] px-2 py-0.5 rounded uppercase font-semibold ${
                        app.is_sandbox ? "bg-amber-100 text-amber-800" : "bg-emerald-100 text-emerald-800"
                      }`}
                    >
                      {app.is_sandbox ? "Sandbox" : "Production"}
                    </span>
                  </div>
                  <button
                    onClick={() => onGenerateKey && onGenerateKey(app.id)}
                    className="text-xs text-sky-700 hover:text-sky-900 font-medium"
                  >
                    + {labels.generateKey}
                  </button>
                </div>

                {/* Credentials */}
                <div className="space-y-1.5">
                  {appCreds.length === 0 ? (
                    <span className="text-[11px] text-gray-400 italic">No API keys generated.</span>
                  ) : (
                    appCreds.map((cred) => (
                      <div
                        key={cred.id}
                        className="flex items-center justify-between p-2 rounded bg-white border border-gray-200 text-xs"
                      >
                        <div>
                          <span className="font-mono text-[11px] font-bold text-gray-800">{cred.client_id}</span>
                          <span className="text-[10px] text-gray-500 block">
                            Secret: {cred.secret_prefix} • Rate Limit: {cred.rate_limit_per_minute}/min
                          </span>
                        </div>
                        {cred.is_active ? (
                          <button
                            onClick={() => onRevokeKey && onRevokeKey(cred.id)}
                            className="text-[10px] text-red-600 hover:text-red-800 font-medium px-2 py-1 bg-red-50 rounded"
                          >
                            Revoke Key
                          </button>
                        ) : (
                          <span className="text-[10px] text-gray-400 uppercase font-semibold">Revoked</span>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
