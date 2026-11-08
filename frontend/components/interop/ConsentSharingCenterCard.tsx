"use client";

import React, { useState } from "react";
import type { DataSharingGrant, IntegrationPartner } from "../../lib/api/types";

interface ConsentSharingCenterCardProps {
  grants: DataSharingGrant[];
  partners: IntegrationPartner[];
  onGrantConsent?: (partnerId: string, purpose: string, categories: string[]) => void;
  onRevokeConsent?: (grantId: string, reason: string) => void;
}

export const ConsentSharingCenterCard: React.FC<ConsentSharingCenterCardProps> = ({
  grants,
  partners,
  onGrantConsent,
  onRevokeConsent,
}) => {
  const [selectedPartnerId, setSelectedPartnerId] = useState<string>(partners[0]?.id || "");
  const [purpose, setPurpose] = useState<string>("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([
    "FARM_PROFILE",
    "OBSERVATIONS",
  ]);

  const toggleCategory = (cat: string) => {
    setSelectedCategories((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-purple-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Farmer Consent & Data Sharing Center</h3>
          <p className="text-xs text-gray-500">
            Granular data authorization with explicit privacy redaction and instant revocation.
          </p>
        </div>
      </div>

      {/* Grant New Authorization */}
      <div className="p-3.5 rounded-lg bg-purple-50/50 border border-purple-100 space-y-3">
        <h4 className="text-xs font-semibold text-gray-800">Authorize Data Access to Verified Partner</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-[11px] font-semibold text-gray-700 mb-1">Select Partner</label>
            <select
              value={selectedPartnerId}
              onChange={(e) => setSelectedPartnerId(e.target.value)}
              className="w-full text-xs p-2 border border-gray-200 rounded bg-white"
            >
              {partners.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.partner_type})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-gray-700 mb-1">Stated Purpose</label>
            <input
              type="text"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              placeholder="e.g. ICAR Soil Health Advisory & Nitrogen Optimization"
              className="w-full text-xs p-2 border border-gray-200 rounded bg-white"
            />
          </div>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-gray-700 mb-1.5">Authorized Data Categories</label>
          <div className="flex flex-wrap gap-2">
            {[
              "FARM_PROFILE",
              "SOIL_HEALTH",
              "WATER_RESOURCES",
              "OBSERVATIONS",
              "DIAGNOSTICS",
              "HARVEST_YIELD",
            ].map((cat) => (
              <label
                key={cat}
                className={`inline-flex items-center text-[11px] px-2.5 py-1 rounded-full border cursor-pointer font-medium transition-colors ${
                  selectedCategories.includes(cat)
                    ? "bg-purple-100 border-purple-400 text-purple-900"
                    : "bg-white border-gray-200 text-gray-600 hover:bg-gray-50"
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedCategories.includes(cat)}
                  onChange={() => toggleCategory(cat)}
                  className="hidden"
                />
                {cat}
              </label>
            ))}
          </div>
        </div>

        <button
          onClick={() => {
            if (selectedPartnerId && purpose.trim() && onGrantConsent) {
              onGrantConsent(selectedPartnerId, purpose.trim(), selectedCategories);
              setPurpose("");
            }
          }}
          disabled={!purpose.trim() || selectedCategories.length === 0}
          className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded text-xs font-semibold shadow-sm transition-colors"
        >
          Authorize Consent Grant
        </button>
      </div>

      {/* Active Grants List */}
      <div className="space-y-2.5 pt-2">
        <h4 className="text-xs font-semibold uppercase text-gray-500 tracking-wider">Active Authorized Grants</h4>
        {grants.length === 0 ? (
          <div className="text-xs text-gray-400 py-3 text-center">No active data sharing grants authorized.</div>
        ) : (
          grants.map((grant) => {
            const partner = partners.find((p) => p.id === grant.partner_id);
            let categories: string[] = [];
            try {
              categories = JSON.parse(grant.data_categories_json || "[]");
            } catch (e) {
              categories = [];
            }

            return (
              <div
                key={grant.id}
                className="p-3 rounded-lg border border-gray-100 bg-gray-50/50 flex items-start justify-between text-xs space-y-1"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-gray-900">{partner?.name || "Integration Partner"}</span>
                    <span
                      className={`text-[9px] px-2 py-0.5 rounded font-semibold uppercase ${
                        grant.is_revoked
                          ? "bg-gray-200 text-gray-700"
                          : "bg-emerald-100 text-emerald-800"
                      }`}
                    >
                      {grant.is_revoked ? "Revoked" : "Active"}
                    </span>
                  </div>
                  <p className="text-gray-600 text-[11px]">Purpose: {grant.purpose}</p>
                  <div className="flex flex-wrap gap-1 pt-1">
                    {categories.map((c) => (
                      <span
                        key={c}
                        className="px-2 py-0.5 bg-white border border-gray-200 rounded text-[9px] text-gray-600 font-mono"
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                </div>

                {!grant.is_revoked && onRevokeConsent && (
                  <button
                    onClick={() => onRevokeConsent(grant.id, "Farmer revoked access")}
                    className="text-[10px] text-red-600 hover:text-red-800 font-medium px-2 py-1 bg-red-50 rounded shrink-0 ml-2"
                  >
                    Revoke Access
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
