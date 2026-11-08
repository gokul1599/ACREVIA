"use client";

import React, { useState } from "react";
import type { ProduceLot, ProduceLotPublic } from "../../lib/api/types";

interface TraceabilityCardProps {
  lot: ProduceLot;
  publicView?: ProduceLotPublic;
  onVerifyPublic?: (qrToken: string) => Promise<void>;
  labels: {
    title: string;
    subtitle: string;
    lotCode: string;
    scanQR: string;
    publicVerification: string;
    overallGrade: string;
    privacyNotice: string;
  };
}

export const TraceabilityCard: React.FC<TraceabilityCardProps> = ({
  lot,
  publicView,
  onVerifyPublic,
  labels,
}) => {
  const [showPublicModal, setShowPublicModal] = useState(false);
  const [loadingPublic, setLoadingPublic] = useState(false);

  const handleOpenPublicView = async () => {
    setShowPublicModal(true);
    if (onVerifyPublic && !publicView) {
      setLoadingPublic(true);
      try {
        await onVerifyPublic(lot.qr_token);
      } finally {
        setLoadingPublic(false);
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-6 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">{labels.title}</h2>
          <p className="text-sm text-slate-500">{labels.subtitle}</p>
        </div>
        <button
          onClick={handleOpenPublicView}
          className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-sm transition gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
          </svg>
          {labels.scanQR} / Preview Public QR
        </button>
      </div>

      {/* Lot Summary Card */}
      <div className="p-5 bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-xl space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div>
            <span className="text-[10px] font-mono tracking-widest text-emerald-400 uppercase">ACREVIA VERIFIED PRODUCE LOT</span>
            <div className="text-xl font-mono font-black mt-0.5">{lot.lot_code}</div>
          </div>
          <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold rounded-full">
            {lot.current_status}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-3 border-t border-slate-700/60 text-xs">
          <div>
            <span className="text-slate-400 block">Commodity</span>
            <span className="font-bold text-white capitalize">{lot.crop_id}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Harvest Date</span>
            <span className="font-mono text-white">{lot.harvest_date}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Initial Lot Qty</span>
            <span className="font-mono text-white font-bold">{parseFloat(lot.initial_quantity).toFixed(1)} {lot.unit}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Remaining Balance</span>
            <span className="font-mono text-emerald-400 font-bold">{parseFloat(lot.remaining_quantity).toFixed(1)} {lot.unit}</span>
          </div>
        </div>
      </div>

      {/* Movement History */}
      {lot.movements && lot.movements.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Chain of Custody & Lot Movements</h3>
          <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
            {lot.movements.map((m) => (
              <div key={m.id} className="p-3 bg-white flex justify-between items-center text-xs">
                <div>
                  <span className="font-bold text-slate-800 uppercase text-[11px] mr-2 px-1.5 py-0.5 rounded bg-slate-100">
                    {m.movement_type}
                  </span>
                  <span className="text-slate-600">{m.source_location} → {m.destination_location}</span>
                  {m.notes && <p className="text-[11px] text-slate-400 mt-0.5">{m.notes}</p>}
                </div>
                <div className="text-right">
                  <div className="font-mono font-bold text-slate-900">
                    {parseFloat(m.quantity_transferred).toFixed(1)} {m.unit}
                  </div>
                  <span className="text-[10px] text-slate-400">{m.movement_timestamp.split("T")[0]}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Public QR Code Modal */}
      {showPublicModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">Public Consumer & Buyer Verification</span>
                <h3 className="text-lg font-black text-slate-900 mt-0.5">{labels.publicVerification}</h3>
              </div>
              <button
                onClick={() => setShowPublicModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            {loadingPublic ? (
              <div className="p-12 text-center text-slate-400">Loading verifiable provenance...</div>
            ) : (
              <div className="space-y-4">
                {/* QR Code Placeholder Graphic */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-center">
                  <div className="text-center space-y-2">
                    <div className="w-32 h-32 mx-auto bg-white border-2 border-slate-900 p-2 rounded-lg flex items-center justify-center shadow-inner">
                      <div className="w-full h-full border border-dashed border-slate-400 flex flex-col items-center justify-center text-[10px] font-mono text-slate-600">
                        <span>QR CODE</span>
                        <span className="text-[8px] text-indigo-600 font-bold mt-1">TOKEN VERIFIED</span>
                      </div>
                    </div>
                    <span className="text-xs font-mono text-slate-500 block">{lot.lot_code}</span>
                  </div>
                </div>

                {publicView && (
                  <div className="space-y-2 text-xs bg-indigo-50/50 p-4 rounded-xl border border-indigo-100">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Crop & Variety:</span>
                      <span className="font-bold text-slate-900">{publicView.crop_name} • {publicView.variety}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Harvest Date:</span>
                      <span className="font-mono text-slate-900">{publicView.harvest_date}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Region:</span>
                      <span className="text-slate-900">{publicView.district}, {publicView.state}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">{labels.overallGrade}:</span>
                      <span className="font-bold text-indigo-700">{publicView.overall_grade}</span>
                    </div>
                  </div>
                )}

                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2">
                  <svg className="w-4 h-4 text-amber-700 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-[11px] text-amber-900 leading-tight">
                    {labels.privacyNotice}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
