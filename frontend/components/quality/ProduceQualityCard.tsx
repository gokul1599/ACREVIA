"use client";

import React, { useState } from "react";
import type { QualityMeasurement, StorageLot } from "../../lib/api/types";

interface ProduceQualityCardProps {
  measurements: QualityMeasurement[];
  storageLots?: StorageLot[];
  lotCode?: string;
  onRecordMeasurement?: (data: {
    parameter_name: string;
    measured_value: number;
    unit: string;
    measurement_method: string;
    instrument_details?: string;
  }) => Promise<void>;
  labels: {
    title: string;
    subtitle: string;
    recordMeasurement: string;
    parameter: string;
    measuredValue: string;
    method: string;
    storageFacility: string;
  };
}

export const ProduceQualityCard: React.FC<ProduceQualityCardProps> = ({
  measurements,
  storageLots = [],
  lotCode,
  onRecordMeasurement,
  labels,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [param, setParam] = useState("MOISTURE_PCT");
  const [value, setValue] = useState<number | "">("");
  const [unit, setUnit] = useState("%");
  const [method, setMethod] = useState("MEASURED_DIGITAL_SENSOR");
  const [instrument, setInstrument] = useState("AgroSens Digital Pin Moisture Meter");

  const handleParamChange = (p: string) => {
    setParam(p);
    if (p === "MOISTURE_PCT") {
      setUnit("%");
      setInstrument("AgroSens Pin Moisture Meter");
    } else if (p === "STAPLE_LENGTH_MM") {
      setUnit("mm");
      setInstrument("Manual Staple Gauge / APMC Lab");
    } else if (p === "ASTA_COLOR") {
      setUnit("ASTA");
      setInstrument("Spectrophotometer Assay");
    } else {
      setUnit("%");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!value || value < 0) return;
    if (onRecordMeasurement) {
      await onRecordMeasurement({
        parameter_name: param,
        measured_value: Number(value),
        unit,
        measurement_method: method,
        instrument_details: instrument || undefined,
      });
      setShowModal(false);
      setValue("");
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-6 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">{labels.title}</h2>
          <p className="text-sm text-slate-500">
            {labels.subtitle} {lotCode && `• Lot: ${lotCode}`}
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg shadow-sm transition"
        >
          + {labels.recordMeasurement}
        </button>
      </div>

      {/* Measurement Table */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Quality Assays & Laboratory Testing</h3>
        {measurements.length === 0 ? (
          <div className="p-6 text-center text-slate-400 bg-slate-50 rounded-lg">
            No quality measurements recorded for this produce lot yet. Record moisture or staple length tests to certify quality.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {measurements.map((m) => (
              <div key={m.id} className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2">
                <div className="flex justify-between items-start">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
                    {m.parameter_name.replace("_", " ")}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-medium ${
                    m.measurement_method === "VERIFIED_LAB_ASSAY"
                      ? "bg-purple-100 text-purple-800"
                      : m.measurement_method === "MEASURED_DIGITAL_SENSOR"
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-slate-200 text-slate-700"
                  }`}>
                    {m.measurement_method}
                  </span>
                </div>
                <div className="text-2xl font-black text-slate-900 font-mono">
                  {parseFloat(m.measured_value).toFixed(1)} {m.unit}
                </div>
                {m.instrument_details && (
                  <p className="text-[11px] text-slate-500">Instrument: {m.instrument_details}</p>
                )}
                <span className="text-[10px] text-slate-400 block">Assayed at {m.measured_at.split("T")[0]}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Storage Lots */}
      {storageLots.length > 0 && (
        <div className="pt-4 border-t border-slate-100 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">{labels.storageFacility}</h3>
          <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
            {storageLots.map((s) => (
              <div key={s.id} className="p-3 bg-white flex justify-between items-center text-xs">
                <div>
                  <span className="font-semibold text-slate-800">Storage Lot #{s.id.slice(0, 8)}</span>
                  <span className="text-slate-400 ml-2">Entry: {s.entry_date}</span>
                </div>
                <div className="font-mono font-bold text-slate-900">
                  {parseFloat(s.quantity_stored).toFixed(1)} {s.unit} ({s.current_status})
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assay Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-800">{labels.recordMeasurement}</h3>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700">{labels.parameter}</label>
                <select
                  value={param}
                  onChange={(e) => handleParamChange(e.target.value)}
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                >
                  <option value="MOISTURE_PCT">Moisture Content (%)</option>
                  <option value="STAPLE_LENGTH_MM">Staple Length (mm) [Cotton]</option>
                  <option value="MICRONAIRE">Micronaire Fineness [Cotton]</option>
                  <option value="ASTA_COLOR">ASTA Color Value [Chilli]</option>
                  <option value="FOREIGN_MATTER_PCT">Foreign Matter / Trash (%)</option>
                  <option value="BROKEN_GRAIN_PCT">Broken Grain Ratio (%) [Rice]</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700">{labels.measuredValue}</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    required
                    value={value}
                    onChange={(e) => setValue(Number(e.target.value))}
                    className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700">Unit</label>
                  <input
                    type="text"
                    disabled
                    value={unit}
                    className="mt-1 w-full bg-slate-100 border border-slate-300 rounded-lg p-2 text-sm text-slate-600"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700">{labels.method}</label>
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                >
                  <option value="MEASURED_DIGITAL_SENSOR">Digital Sensor (e.g. Pin Meter)</option>
                  <option value="VERIFIED_LAB_ASSAY">Certified Laboratory Assay (APMC / Govt)</option>
                  <option value="FARMER_VISUAL_ESTIMATE">Farmer Visual Estimate</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700">Testing Device / Laboratory Details</label>
                <input
                  type="text"
                  value={instrument}
                  onChange={(e) => setInstrument(e.target.value)}
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                />
              </div>
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
                  Save Assay
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
