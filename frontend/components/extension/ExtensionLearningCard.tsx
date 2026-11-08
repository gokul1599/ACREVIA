"use client";

import React, { useState } from "react";
import type { LearningResource, TrainingEvent } from "../../lib/api/types";

interface ExtensionLearningCardProps {
  resource?: LearningResource;
  event?: TrainingEvent;
  onRegisterEvent?: (eventId: string) => Promise<void>;
  onFeedback?: (resourceId: string, feedbackType: string) => Promise<void>;
  labels: {
    title: string;
    learningResources: string;
    trainingEvents: string;
    registerEvent: string;
    capacityNotice: string;
    feedbackHelpful: string;
  };
}

export const ExtensionLearningCard: React.FC<ExtensionLearningCardProps> = ({
  resource,
  event,
  onRegisterEvent,
  onFeedback,
  labels,
}) => {
  const [registered, setRegistered] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);

  const handleRegister = async () => {
    if (event && onRegisterEvent && !registered) {
      await onRegisterEvent(event.id);
      setRegistered(true);
    }
  };

  const handleFeedback = async () => {
    if (resource && onFeedback && !feedbackSent) {
      await onFeedback(resource.id, "HELPFUL");
      setFeedbackSent(true);
    }
  };

  if (resource) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-3 hover:border-emerald-300 transition-colors">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                {resource.resource_type}
              </span>
              {resource.crop_id && (
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                  {resource.crop_id.toUpperCase()}
                </span>
              )}
              <span className="text-xs text-gray-500 uppercase">Lang: {resource.language}</span>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mt-2">{resource.title}</h3>
          </div>
          <span className="text-xs text-gray-400">👁 {resource.view_count} views</span>
        </div>

        <p className="text-gray-700 text-sm whitespace-pre-line leading-relaxed">{resource.content_body}</p>

        <div className="pt-2 border-t border-gray-100 flex items-center justify-between">
          <span className="text-xs text-gray-500">Official Extension Guide</span>
          {onFeedback && (
            <button
              type="button"
              onClick={handleFeedback}
              disabled={feedbackSent}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
                feedbackSent
                  ? "bg-emerald-50 text-emerald-700 border-emerald-300 cursor-default"
                  : "bg-gray-50 text-gray-700 border-gray-300 hover:bg-emerald-50 hover:text-emerald-700"
              }`}
            >
              👍 {feedbackSent ? "Feedback Recorded" : labels.feedbackHelpful}
            </button>
          )}
        </div>
      </div>
    );
  }

  if (event) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-3 hover:border-emerald-300 transition-colors">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-sky-50 text-sky-800 border border-sky-200">
                {event.event_type}
              </span>
              <span className="text-xs text-gray-500">📍 {event.district}</span>
              {event.is_online && (
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-50 text-blue-800 border border-blue-200">
                  Online Webinar
                </span>
              )}
            </div>
            <h3 className="text-lg font-bold text-gray-900 mt-2">{event.title}</h3>
          </div>
          <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
            {event.status}
          </span>
        </div>

        <p className="text-gray-700 text-sm">{event.description}</p>

        <div className="bg-gray-50 p-3 rounded-lg text-xs space-y-1 text-gray-700">
          <div className="flex justify-between">
            <span>Start:</span>
            <strong>{new Date(event.scheduled_start).toLocaleString()}</strong>
          </div>
          <div className="flex justify-between">
            <span>{labels.capacityNotice}:</span>
            <span>Max {event.max_capacity} attendees</span>
          </div>
        </div>

        {onRegisterEvent && (
          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={handleRegister}
              disabled={registered}
              className={`px-4 py-2 text-xs font-semibold rounded-lg transition-colors ${
                registered
                  ? "bg-emerald-100 text-emerald-800 cursor-default"
                  : "bg-emerald-600 text-white hover:bg-emerald-700"
              }`}
            >
              {registered ? "✓ Registered" : labels.registerEvent}
            </button>
          </div>
        )}
      </div>
    );
  }

  return null;
};
