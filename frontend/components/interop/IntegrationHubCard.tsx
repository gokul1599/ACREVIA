"use client";

import React, { useState } from "react";
import type { IntegrationPartner, PartnerIntegration } from "../../lib/api/types";

interface IntegrationHubCardProps {
  partners: IntegrationPartner[];
  integrations: PartnerIntegration[];
  labels: {
    title: string;
    subtitle: string;
    registeredPartners: string;
    registerPartner: string;
    verificationStatus: string;
    verified: string;
    underReview: string;
  };
  onRegisterClick?: () => void;
}

export const IntegrationHubCard: React.FC<IntegrationHubCardProps> = ({
  partners,
  integrations,
  labels,
  onRegisterClick,
}) => {
  const [filterType, setFilterType] = useState<string>("ALL");

  const filteredPartners = filterType === "ALL"
    ? partners
    : partners.filter((p) => p.partner_type === filterType);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">{labels.subtitle}</p>
        </div>
        <button
          onClick={onRegisterClick}
          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
        >
          {labels.registerPartner}
        </button>
      </div>

      <div className="flex gap-2 text-xs overflow-x-auto pb-1">
        {["ALL", "LABORATORY", "UNIVERSITY", "WEATHER_PROVIDER", "IOT_MANUFACTURER"].map((type) => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`px-2.5 py-1 rounded-full border text-[11px] font-medium transition-colors ${
              filterType === type
                ? "bg-emerald-50 border-emerald-500 text-emerald-800"
                : "border-gray-200 text-gray-600 hover:bg-gray-50"
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filteredPartners.length === 0 ? (
          <div className="text-center py-6 text-gray-400 text-xs">
            No integration partners found for this filter.
          </div>
        ) : (
          filteredPartners.map((partner) => {
            const partnerIntegrations = integrations.filter((i) => i.partner_id === partner.id);
            const isVerified = partner.verification_status === "VERIFIED";

            return (
              <div
                key={partner.id}
                className="p-3.5 rounded-lg border border-gray-100 hover:border-emerald-200 bg-gray-50/50 space-y-2 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900">{partner.name}</h4>
                    <span className="text-[10px] text-gray-500 block">
                      {partner.partner_type} • {partner.contact_email}
                    </span>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                      isVerified
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {isVerified ? labels.verified : labels.underReview}
                  </span>
                </div>

                {partner.description && (
                  <p className="text-xs text-gray-600 line-clamp-2">{partner.description}</p>
                )}

                {partnerIntegrations.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {partnerIntegrations.map((pi) => (
                      <span
                        key={pi.id}
                        className="inline-flex items-center px-2 py-0.5 rounded-md bg-white border border-gray-200 text-[10px] font-medium text-gray-700"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>
                        {pi.display_name} ({pi.connector_type})
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
