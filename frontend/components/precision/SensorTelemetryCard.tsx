"use client";

import React from "react";
import type { SensorMeasurement } from "../../lib/api/types";

interface SensorTelemetryCardProps {
  measurement?: SensorMeasurement | null;
  labels: {
    title: string;
    soilMoisture: string;
    leafWetness: string;
    stuckSensorAlert: string;
    uncalibratedWarning: string;
  };
}

export const SensorTelemetryCard: React.FC<SensorTelemetryCardProps> = ({
  measurement,
  labels,
}) => {
  const isStuck = measurement?.data_quality_flag === "SUSPECT_STUCK";
  const isUncalibrated = measurement?.data_quality_flag === "UNCALIBRATED";

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-100">
        <div>
          <h3 className="font-semibold text-neutral-900">{labels.title}</h3>
          <p className="text-xs text-neutral-500">In-situ Field Probes</p>
        </div>
        {measurement && (
          <span
            className={`px-2 py-0.5 text-xs font-medium rounded ${
              measurement.data_quality_flag === "VALID"
                ? "bg-emerald-50 text-emerald-700"
                : "bg-amber-50 text-amber-700"
            }`}
          >
            {measurement.data_quality_flag}
          </span>
        )}
      </div>

      {isStuck && (
        <div className="mt-3 rounded-lg bg-rose-50 p-2.5 border border-rose-200 text-xs text-rose-800">
          {labels.stuckSensorAlert}
        </div>
      )}

      {isUncalibrated && (
        <div className="mt-3 rounded-lg bg-amber-50 p-2.5 border border-amber-200 text-xs text-amber-800">
          {labels.uncalibratedWarning}
        </div>
      )}

      {measurement ? (
        <div className="mt-4 grid grid-cols-2 gap-3 text-center">
          <div className="rounded-lg bg-neutral-50 p-3 border border-neutral-100">
            <span className="text-xs text-neutral-500 block">{labels.soilMoisture}</span>
            <span className="text-xl font-bold text-neutral-900">
              {measurement.soil_moisture_pct !== undefined ? `${measurement.soil_moisture_pct.toFixed(1)}%` : "—"}
            </span>
          </div>
          <div className="rounded-lg bg-neutral-50 p-3 border border-neutral-100">
            <span className="text-xs text-neutral-500 block">{labels.leafWetness}</span>
            <span className="text-xl font-bold text-neutral-900">
              {measurement.leaf_wetness_pct !== undefined ? `${measurement.leaf_wetness_pct.toFixed(0)}%` : "—"}
            </span>
          </div>
          <div className="rounded-lg bg-neutral-50 p-3 border border-neutral-100">
            <span className="text-xs text-neutral-500 block">Soil Temp</span>
            <span className="text-base font-semibold text-neutral-800">
              {measurement.soil_temperature_c !== undefined ? `${measurement.soil_temperature_c.toFixed(1)}°C` : "—"}
            </span>
          </div>
          <div className="rounded-lg bg-neutral-50 p-3 border border-neutral-100">
            <span className="text-xs text-neutral-500 block">Ambient Temp</span>
            <span className="text-base font-semibold text-neutral-800">
              {measurement.ambient_temperature_c !== undefined ? `${measurement.ambient_temperature_c.toFixed(1)}°C` : "—"}
            </span>
          </div>
        </div>
      ) : (
        <div className="py-6 text-center text-sm text-neutral-500">
          No live sensor nodes streaming telemetry for this plot.
        </div>
      )}
    </div>
  );
};
