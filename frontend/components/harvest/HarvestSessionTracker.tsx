"use client";

import React, { useState } from "react";
import type { HarvestSession, HarvestPlan } from "../../lib/api/types";

interface HarvestSessionTrackerProps {
  sessions: HarvestSession[];
  plan?: HarvestPlan;
  onRecordSession?: (data: {
    picking_number: number;
    harvest_date: string;
    harvested_quantity: number;
    unit: string;
    loss_quantity: number;
    notes?: string;
  }) => Promise<void>;
  labels: {
    title: string;
    subtitle: string;
    newPlan: string;
    recordSession: string;
    pickingIndex: string;
    harvestedQty: string;
    fieldLoss: string;
    mintedLot: string;
  };
}

export const HarvestSessionTracker: React.FC<HarvestSessionTrackerProps> = ({
  sessions,
  plan,
  onRecordSession,
  labels,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [pickingNumber, setPickingNumber] = useState<number>(sessions.length + 1);
  const [harvestDate, setHarvestDate] = useState(new Date().toISOString().split("T")[0]);
  const [quantity, setQuantity] = useState<number | "">("");
  const [loss, setLoss] = useState<number>(0);
  const [notes, setNotes] = useState("");

  const totalHarvested = sessions.reduce((sum, s) => sum + parseFloat(s.harvested_quantity || "0"), 0);
  const totalLoss = sessions.reduce((sum, s) => sum + parseFloat(s.loss_quantity || "0"), 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quantity || quantity <= 0) return;
    if (onRecordSession) {
      await onRecordSession({
        picking_number: pickingNumber,
        harvest_date: harvestDate,
        harvested_quantity: Number(quantity),
        unit: "QUINTAL",
        loss_quantity: Number(loss),
        notes: notes || undefined,
      });
      setShowModal(false);
      setQuantity("");
      setNotes("");
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
          onClick={() => {
            setPickingNumber(sessions.length + 1);
            setShowModal(true);
          }}
          className="inline-flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg shadow-sm transition"
        >
          + {labels.recordSession}
        </button>
      </div>

      {/* Harvest Aggregate Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
          <span className="text-xs font-semibold uppercase text-emerald-700">Total Harvested</span>
          <p className="text-2xl font-black text-emerald-950 mt-1 font-mono">{totalHarvested.toFixed(2)} Qtl</p>
          <span className="text-xs text-emerald-700">{sessions.length} picking sessions recorded</span>
        </div>
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <span className="text-xs font-semibold uppercase text-amber-700">Field & Shattering Loss</span>
          <p className="text-2xl font-black text-amber-950 mt-1 font-mono">{totalLoss.toFixed(2)} Qtl</p>
          <span className="text-xs text-amber-700">
            {totalHarvested > 0 ? ((totalLoss / (totalHarvested + totalLoss)) * 100).toFixed(1) : 0}% harvest loss
          </span>
        </div>
        <div className="p-4 bg-sky-50 border border-sky-200 rounded-lg">
          <span className="text-xs font-semibold uppercase text-sky-700">Planned Target</span>
          <p className="text-2xl font-black text-sky-950 mt-1 font-mono">
            {plan ? `${parseFloat(plan.estimated_quantity_quintals).toFixed(1)} Qtl` : "In Progress"}
          </p>
          <span className="text-xs text-sky-700">
            {plan ? `Target completion by ${plan.planned_end_date}` : "Dynamic multi-session tracking"}
          </span>
        </div>
      </div>

      {/* Session Timeline */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Recorded Picking Sessions</h3>
        {sessions.length === 0 ? (
          <div className="p-6 text-center text-slate-400 bg-slate-50 rounded-lg">
            No picking sessions recorded yet. Start tracking your first cotton picking or paddy harvest.
          </div>
        ) : (
          <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
            {sessions.map((s) => (
              <div key={s.id} className="p-4 bg-white flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 hover:bg-slate-50 transition">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="inline-block px-2 py-0.5 text-xs font-bold rounded bg-emerald-100 text-emerald-800">
                      Picking #{s.picking_number}
                    </span>
                    <span className="text-xs text-slate-500">{s.harvest_date}</span>
                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
                      {s.quantity_type}
                    </span>
                  </div>
                  {s.notes && <p className="text-xs text-slate-600 mt-1">{s.notes}</p>}
                </div>
                <div className="text-right">
                  <div className="text-lg font-black text-slate-900 font-mono">
                    {parseFloat(s.harvested_quantity).toFixed(2)} {s.unit}
                  </div>
                  {parseFloat(s.loss_quantity) > 0 && (
                    <span className="text-xs text-amber-600">Loss: {parseFloat(s.loss_quantity).toFixed(2)} {s.unit}</span>
                  )}
                  {s.lot_code && (
                    <div className="text-[11px] font-mono text-emerald-700 font-semibold">
                      Lot: {s.lot_code}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Record Session Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-800">{labels.recordSession}</h3>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700">{labels.pickingIndex}</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={pickingNumber}
                    onChange={(e) => setPickingNumber(Number(e.target.value))}
                    className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700">Harvest Date</label>
                  <input
                    type="date"
                    required
                    value={harvestDate}
                    onChange={(e) => setHarvestDate(e.target.value)}
                    className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700">{labels.harvestedQty}</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.1"
                    required
                    value={quantity}
                    onChange={(e) => setQuantity(Number(e.target.value))}
                    className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700">{labels.fieldLoss}</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={loss}
                    onChange={(e) => setLoss(Number(e.target.value))}
                    className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm font-mono"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700">Session Notes & Quality Observations</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. 1st cotton picking, boll opening complete, clean picking with minimal trash"
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                />
              </div>
              <p className="text-[11px] text-slate-500">
                Recording a harvest session automatically mints a unique ACREVIA Produce Lot for downstream traceability and quality testing.
              </p>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium"
                >
                  Save & Mint Lot
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
