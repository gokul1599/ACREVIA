"use client";

import React, { useState } from "react";
import type { CommunityPost } from "../../lib/api/types";

interface CommunityDiscussionCardProps {
  post: CommunityPost;
  onVoteHelpful?: (postId: string) => Promise<void>;
  onAddComment?: (postId: string, content: string) => Promise<void>;
  onReport?: (postId: string, reason: string) => Promise<void>;
  labels: {
    title: string;
    expertReplyBadge: string;
    helpfulVote: string;
    helpfulDisclaimer: string;
    reportContent: string;
  };
}

export const CommunityDiscussionCard: React.FC<CommunityDiscussionCardProps> = ({
  post,
  onVoteHelpful,
  onAddComment,
  onReport,
  labels,
}) => {
  const [newComment, setNewComment] = useState("");
  const [submittingComment, setSubmittingComment] = useState(false);
  const [hasVoted, setHasVoted] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState("MISINFORMATION");

  const handleHelpfulClick = async () => {
    if (onVoteHelpful && !hasVoted) {
      await onVoteHelpful(post.id);
      setHasVoted(true);
    }
  };

  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || !onAddComment) return;
    setSubmittingComment(true);
    try {
      await onAddComment(post.id, newComment);
      setNewComment("");
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleReportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (onReport) {
      await onReport(post.id, reportReason);
      setShowReportModal(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-4 hover:border-emerald-300 transition-colors">
      {/* Post Header */}
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
              {post.post_type}
            </span>
            {post.crop_id && (
              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                {post.crop_id.toUpperCase()}
              </span>
            )}
            {post.is_expert_reviewed && (
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 border border-blue-300 flex items-center gap-1">
                ✓ {labels.expertReplyBadge}
              </span>
            )}
          </div>
          <h3 className="text-lg font-bold text-gray-900 mt-2">{post.title}</h3>
        </div>
        <button
          type="button"
          onClick={() => setShowReportModal(true)}
          className="text-xs text-gray-400 hover:text-rose-600 transition-colors p-1"
          title={labels.reportContent}
          aria-label={labels.reportContent}
        >
          🚩
        </button>
      </div>

      {/* Post Body */}
      <p className="text-gray-700 text-sm whitespace-pre-line leading-relaxed">{post.content}</p>

      {/* Helpful Vote & Scientific Disclaimer */}
      <div className="pt-2 border-t border-gray-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleHelpfulClick}
            disabled={hasVoted}
            className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all flex items-center gap-1.5 ${
              hasVoted
                ? "bg-emerald-50 text-emerald-700 border-emerald-300 cursor-default"
                : "bg-gray-50 text-gray-700 border-gray-300 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-400"
            }`}
          >
            👍 {labels.helpfulVote} ({post.helpful_count + (hasVoted ? 1 : 0)})
          </button>
        </div>
        <p className="text-[11px] text-gray-500 italic max-w-sm">
          {labels.helpfulDisclaimer}
        </p>
      </div>

      {/* Comments List */}
      {post.comments && post.comments.length > 0 && (
        <div className="mt-3 space-y-2 bg-gray-50 rounded-lg p-3">
          <h4 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Replies</h4>
          {post.comments.map((comment) => (
            <div
              key={comment.id}
              className={`p-2.5 rounded-md text-xs space-y-1 ${
                comment.is_expert_reply
                  ? "bg-blue-50 border border-blue-200 text-blue-950"
                  : "bg-white border border-gray-200 text-gray-800"
              }`}
            >
              {comment.is_expert_reply && (
                <div className="flex items-center gap-1 font-semibold text-blue-700">
                  <span>★</span> {labels.expertReplyBadge}
                </div>
              )}
              <p className="leading-normal">{comment.content}</p>
            </div>
          ))}
        </div>
      )}

      {/* Add Comment Input */}
      {onAddComment && (
        <form onSubmit={handleCommentSubmit} className="flex gap-2 pt-2">
          <input
            type="text"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a farmer reply or observation..."
            className="flex-1 px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500"
            disabled={submittingComment}
          />
          <button
            type="submit"
            disabled={submittingComment || !newComment.trim()}
            className="px-3 py-2 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 disabled:opacity-50"
          >
            Reply
          </button>
        </form>
      )}

      {/* Report Modal */}
      {showReportModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-sm w-full p-5 space-y-4 shadow-xl">
            <h4 className="text-base font-bold text-gray-900">{labels.reportContent}</h4>
            <form onSubmit={handleReportSubmit} className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-700 block mb-1">Reason</label>
                <select
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  className="w-full text-xs p-2 border border-gray-300 rounded-lg"
                >
                  <option value="MISINFORMATION">Misinformation / Unverified Advice</option>
                  <option value="DANGEROUS_ADVICE">Dangerous Chemical or Practice</option>
                  <option value="SPAM">Commercial Spam</option>
                  <option value="HARASSMENT">Harassment or Abuse</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowReportModal(false)}
                  className="px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3 py-1.5 text-xs bg-rose-600 text-white font-medium rounded-lg hover:bg-rose-700"
                >
                  Submit Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
