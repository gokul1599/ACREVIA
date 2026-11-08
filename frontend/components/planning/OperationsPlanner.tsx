"use client";

import React, { useState } from "react";
import type { CropTask } from "../../lib/api/types";

interface OperationsPlannerProps {
  tasks: CropTask[];
  onCompleteTask?: (taskId: string, details: { labor_hours?: number; materials_used?: any[]; observations?: string }) => Promise<void>;
  labels: {
    title: string;
    calendars: string;
    tasks: string;
    weatherConflict: string;
    rescheduleAdvice: string;
    completeTask: string;
    materials: string;
    laborHours: string;
  };
}

export const OperationsPlanner: React.FC<OperationsPlannerProps> = ({
  tasks,
  onCompleteTask,
  labels,
}) => {
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const [laborHours, setLaborHours] = useState<number>(3.5);
  const [notes, setNotes] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);

  const handleComplete = async (taskId: string) => {
    if (!onCompleteTask || submitting) return;
    setSubmitting(true);
    try {
      await onCompleteTask(taskId, {
        labor_hours: laborHours,
        observations: notes,
      });
      setSelectedTask(null);
      setNotes("");
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "bg-emerald-100 text-emerald-800 border-emerald-300";
      case "DUE":
        return "bg-amber-100 text-amber-800 border-amber-300";
      case "IN_PROGRESS":
        return "bg-sky-100 text-sky-800 border-sky-300";
      default:
        return "bg-neutral-100 text-neutral-800 border-neutral-300";
    }
  };

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-neutral-100 pb-3">
        <div>
          <h2 className="text-lg font-bold text-neutral-900">{labels.title}</h2>
          <p className="text-xs text-neutral-500">{tasks.length} Scheduled Operations</p>
        </div>
      </div>

      <div className="space-y-3">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`p-4 rounded-xl border transition-all ${
              task.weather_conflict_flag
                ? "border-rose-300 bg-rose-50/50"
                : "border-neutral-200 bg-white hover:border-neutral-300"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-neutral-900 text-sm">{task.task_name}</span>
                  <span className={`px-2 py-0.5 text-[11px] font-medium rounded-full border ${getStatusColor(task.status)}`}>
                    {task.status}
                  </span>
                </div>
                <p className="text-xs text-neutral-500">
                  Category: {task.task_category} • Due: {task.due_date}
                </p>
              </div>

              {task.status !== "COMPLETED" && onCompleteTask && (
                <button
                  onClick={() => setSelectedTask(selectedTask === task.id ? null : task.id)}
                  className="px-3 py-1 text-xs font-medium bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                >
                  {labels.completeTask}
                </button>
              )}
            </div>

            {/* Weather Conflict Warning */}
            {task.weather_conflict_flag && (
              <div className="mt-3 p-2.5 bg-rose-100 border border-rose-200 rounded-lg text-xs text-rose-800 space-y-1">
                <span className="font-bold block">{labels.weatherConflict}:</span>
                <p>{task.conflict_reason || labels.rescheduleAdvice}</p>
              </div>
            )}

            {/* Completion Form Drawer */}
            {selectedTask === task.id && (
              <div className="mt-3 pt-3 border-t border-neutral-200 text-xs space-y-2">
                <span className="font-semibold text-neutral-800 block">Record Field Execution:</span>
                <div className="flex gap-3">
                  <label className="flex-1">
                    <span className="text-neutral-500 block mb-1">{labels.laborHours}</span>
                    <input
                      type="number"
                      step="0.5"
                      value={laborHours}
                      onChange={(e) => setLaborHours(parseFloat(e.target.value) || 0)}
                      className="w-full px-2.5 py-1.5 rounded border border-neutral-300 text-xs"
                    />
                  </label>
                  <label className="flex-2">
                    <span className="text-neutral-500 block mb-1">Observations / Notes</span>
                    <input
                      type="text"
                      placeholder="e.g. Clean spray coverage, no leaf burn"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="w-full px-2.5 py-1.5 rounded border border-neutral-300 text-xs"
                    />
                  </label>
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    onClick={() => setSelectedTask(null)}
                    className="px-3 py-1 text-xs text-neutral-600 hover:text-neutral-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleComplete(task.id)}
                    disabled={submitting}
                    className="px-3 py-1 text-xs font-medium bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50"
                  >
                    {submitting ? "Saving..." : "Confirm Completion"}
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
