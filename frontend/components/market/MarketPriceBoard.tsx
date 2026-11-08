"use client";

import React, { useState } from "react";
import type { MarketPriceObservation, MarketCompareResponse } from "../../lib/api/types";

interface MarketPriceBoardProps {
  prices: MarketPriceObservation[];
  comparison?: MarketCompareResponse;
  selectedCrop: string;
  onSelectCrop: (cropId: string) => void;
  onRunComparison?: (cropId: string, quantityQuintals: number) => Promise<void>;
  labels: {
    title: string;
    subtitle: string;
    selectCrop: string;
    quantityForSale: string;
    mandiBoard: string;
    modalPrice: string;
    minMaxRange: string;
    netRealizationComparison: string;
    effectiveRate: string;
    transportDeductions: string;
    mandiCess: string;
    marketDisclaimer: string;
  };
}

export const MarketPriceBoard: React.FC<MarketPriceBoardProps> = ({
  prices,
  comparison,
  selectedCrop,
  onSelectCrop,
  onRunComparison,
  labels,
}) => {
  const [quantity, setQuantity] = useState<number>(20);
  const [comparing, setComparing] = useState<boolean>(false);

  const handleCompareClick = async () => {
    if (onRunComparison && quantity > 0) {
      setComparing(true);
      try {
        await onRunComparison(selectedCrop, quantity);
      } finally {
        setComparing(false);
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
        <div className="flex items-center gap-2">
          {["cotton", "rice", "chilli"].map((crop) => (
            <button
              key={crop}
              onClick={() => onSelectCrop(crop)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${
                selectedCrop === crop
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {crop}
            </button>
          ))}
        </div>
      </div>

      {/* Mandi Price Grid */}
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 mb-3">{labels.mandiBoard}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {prices.map((p) => (
            <div key={p.id} className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 hover:border-emerald-300 transition">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-slate-900">{p.market?.market_name || "Mandi"}</h4>
                  <span className="text-xs text-slate-500">{p.market?.district}, {p.market?.state}</span>
                </div>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-mono">
                  {p.source_provider}
                </span>
              </div>
              <div className="mt-4 flex items-baseline justify-between">
                <div>
                  <span className="text-xs text-slate-500 block">{labels.modalPrice}</span>
                  <span className="text-xl font-black text-emerald-700 font-mono">₹{parseFloat(p.modal_price).toFixed(0)}</span>
                  <span className="text-xs text-slate-500 ml-1">/ Qtl</span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 block">{labels.minMaxRange}</span>
                  <span className="text-xs font-mono text-slate-600">₹{parseFloat(p.min_price).toFixed(0)} - ₹{parseFloat(p.max_price).toFixed(0)}</span>
                </div>
              </div>
              <div className="mt-2 pt-2 border-t border-slate-200 flex justify-between text-[11px] text-slate-500">
                <span>Arrival: {parseFloat(p.arrival_quantity_quintals).toFixed(0)} Qtl</span>
                <span>As of {p.observation_date}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comparative Net Realization Engine */}
      <div className="p-5 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h3 className="font-bold text-emerald-950">{labels.netRealizationComparison}</h3>
            <p className="text-xs text-emerald-800">
              Evaluates true net realization across Telangana mandis after adjusting for haulage distance and market fees.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              className="w-24 border border-emerald-300 rounded-lg p-1.5 text-sm font-mono text-center"
              placeholder="Qty (Qtl)"
            />
            <button
              onClick={handleCompareClick}
              disabled={comparing}
              className="px-4 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-bold transition shadow-sm"
            >
              {comparing ? "Calculating..." : "Compare Net Realization"}
            </button>
          </div>
        </div>

        {comparison && comparison.comparisons.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs divide-y divide-emerald-200 text-left bg-white/80 rounded-lg">
              <thead>
                <tr className="text-emerald-900 bg-emerald-100/50">
                  <th className="p-2.5">Mandi Hub</th>
                  <th className="p-2.5">Distance</th>
                  <th className="p-2.5">Modal Price</th>
                  <th className="p-2.5">Transport Est.</th>
                  <th className="p-2.5">Cess & Hamali</th>
                  <th className="p-2.5 text-right font-bold text-emerald-950">{labels.effectiveRate}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-emerald-100">
                {comparison.comparisons.map((c, idx) => (
                  <tr key={c.market_id} className={idx === 0 ? "bg-emerald-50 font-semibold" : ""}>
                    <td className="p-2.5">
                      {c.market_name}
                      {idx === 0 && <span className="ml-2 text-[10px] bg-emerald-600 text-white px-1.5 py-0.2 rounded font-bold">Top Realization</span>}
                    </td>
                    <td className="p-2.5 font-mono">{c.distance_km} km</td>
                    <td className="p-2.5 font-mono">₹{parseFloat(c.modal_price_per_quintal).toFixed(0)}</td>
                    <td className="p-2.5 font-mono text-rose-700">-₹{parseFloat(c.estimated_transport_cost).toFixed(0)}</td>
                    <td className="p-2.5 font-mono text-rose-700">-₹{(parseFloat(c.estimated_mandi_cess) + parseFloat(c.estimated_handling_charges)).toFixed(0)}</td>
                    <td className="p-2.5 text-right font-mono font-bold text-emerald-800 text-sm">
                      ₹{parseFloat(c.effective_rate_per_quintal).toFixed(0)} / Qtl
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <p className="text-[11px] text-emerald-700 italic">
          * {labels.marketDisclaimer}
        </p>
      </div>
    </div>
  );
};
