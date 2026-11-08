import test from "node:test";
import assert from "node:assert";

// Mock localStorage for Node test runner
const mockStorage = new Map();
globalThis.localStorage = {
  getItem: (key) => mockStorage.get(key) || null,
  setItem: (key, val) => mockStorage.set(key, String(val)),
  removeItem: (key) => mockStorage.delete(key),
  clear: () => mockStorage.clear(),
};
globalThis.window = {};

import { OfflineQueue } from "../lib/offline/queue.ts";

test("OfflineQueue - saves draft and assigns client UUID and timestamp", () => {
  localStorage.clear();

  const draft = OfflineQueue.saveDraft({
    type: "OBSERVATION",
    farm_id: "farm-123",
    plot_id: "plot-456",
    notes: "Foliar yellowing on upper leaves",
  });

  assert.ok(draft.id.startsWith("draft-"));
  assert.strictEqual(draft.sync_status, "PENDING");
  assert.strictEqual(draft.farm_id, "farm-123");
  assert.ok(draft.created_at);

  const allDrafts = OfflineQueue.getDrafts();
  assert.strictEqual(allDrafts.length, 1);
  assert.strictEqual(allDrafts[0].id, draft.id);
});

test("OfflineQueue - updates draft status and removes on completion", () => {
  localStorage.clear();

  const draft = OfflineQueue.saveDraft({
    type: "DIAGNOSIS_REQUEST",
    farm_id: "farm-999",
    crop_type: "cotton",
  });

  OfflineQueue.updateDraftStatus(draft.id, "SYNCING");
  let drafts = OfflineQueue.getDrafts();
  assert.strictEqual(drafts[0].sync_status, "SYNCING");

  OfflineQueue.updateDraftStatus(draft.id, "FAILED", "Network timeout");
  drafts = OfflineQueue.getDrafts();
  assert.strictEqual(drafts[0].sync_status, "FAILED");
  assert.strictEqual(drafts[0].error_message, "Network timeout");

  OfflineQueue.removeDraft(draft.id);
  assert.strictEqual(OfflineQueue.getDrafts().length, 0);
});
