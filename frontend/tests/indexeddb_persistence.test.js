// ACREVIA Frontend Offline Persistence & Synchronization Automated Test Suite
import test from "node:test";
import assert from "node:assert";

// Mock localStorage and window for Node test environment
const mockStorage = new Map();
globalThis.localStorage = {
  getItem: (key) => mockStorage.get(key) || null,
  setItem: (key, val) => mockStorage.set(key, String(val)),
  removeItem: (key) => mockStorage.delete(key),
  clear: () => mockStorage.clear(),
};
globalThis.window = {
  localStorage: globalThis.localStorage,
};

import { OfflineDB } from "../lib/offline/db.ts";
import { StorageMigration, LEGACY_STORAGE_KEY, MIGRATION_FLAG_KEY } from "../lib/offline/migration.ts";
import { OfflineQueue } from "../lib/offline/queue.ts";

test("IndexedDB Engine - stores and retrieves structured offline records", async () => {
  await OfflineDB.clearAll();

  const record = {
    id: "rec-test-001",
    tenant_id: "tenant-warangal-01",
    user_id: "user-farmer-01",
    type: "OBSERVATION",
    farm_id: "farm-101",
    crop_type: "cotton",
    notes: "Stem bollworm symptoms observed",
    attachment_ids: ["attach-001"],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    sync_status: "QUEUED",
    idempotency_key: "idemp-rec-test-001",
    retry_count: 0,
    version: 1,
  };

  await OfflineDB.putRecord(record);
  const retrieved = await OfflineDB.getRecord("rec-test-001");

  assert.ok(retrieved);
  assert.strictEqual(retrieved.id, "rec-test-001");
  assert.strictEqual(retrieved.tenant_id, "tenant-warangal-01");
  assert.strictEqual(retrieved.crop_type, "cotton");
  assert.strictEqual(retrieved.sync_status, "QUEUED");
});

test("IndexedDB Engine - stores binary attachments with MIME and size metadata", async () => {
  await OfflineDB.clearAll();

  const attachment = {
    id: "attach-001",
    record_id: "rec-test-001",
    filename: "bollworm_leaf.jpg",
    mime_type: "image/jpeg",
    size_bytes: 2048500, // ~2MB
    created_at: new Date().toISOString(),
    is_uploaded: false,
  };

  await OfflineDB.putAttachment(attachment);
  const retrieved = await OfflineDB.getAttachment("attach-001");

  assert.ok(retrieved);
  assert.strictEqual(retrieved.id, "attach-001");
  assert.strictEqual(retrieved.record_id, "rec-test-001");
  assert.strictEqual(retrieved.size_bytes, 2048500);

  const attachments = await OfflineDB.getAttachmentsForRecord("rec-test-001");
  assert.strictEqual(attachments.length, 1);
  assert.strictEqual(attachments[0].id, "attach-001");
});

test("StorageMigration - safely migrates legacy localStorage drafts to IndexedDB", async () => {
  await OfflineDB.clearAll();
  localStorage.clear();

  const legacyDrafts = [
    {
      id: "legacy-draft-1",
      type: "OBSERVATION",
      farm_id: "farm-nalgonda-01",
      plot_id: "plot-01",
      notes: "Leaf blast symptoms on paddy",
      image_data_base64: "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
      image_filename: "paddy_blast.jpg",
      created_at: "2026-11-01T10:00:00Z",
      sync_status: "PENDING",
    },
    {
      id: "legacy-draft-2",
      type: "DIAGNOSIS_REQUEST",
      farm_id: "farm-nalgonda-02",
      crop_type: "chilli",
      notes: "Leaf curl virus suspect",
      created_at: "2026-11-01T11:00:00Z",
      sync_status: "FAILED",
      error_message: "Network unreachable",
    },
  ];

  localStorage.setItem(LEGACY_STORAGE_KEY, JSON.stringify(legacyDrafts));
  assert.strictEqual(StorageMigration.isMigrationNeeded(), true);

  const result = await StorageMigration.migrateLegacyStorage();
  assert.strictEqual(result.success, true);
  assert.strictEqual(result.migrated_count, 2);
  assert.strictEqual(result.attachment_count, 1);

  // Migration flag set
  assert.strictEqual(localStorage.getItem(MIGRATION_FLAG_KEY), "true");

  // Verify records in IndexedDB
  const allRecords = await OfflineDB.getAllRecords();
  assert.strictEqual(allRecords.length, 2);

  const migrated1 = await OfflineDB.getRecord("legacy-draft-1");
  assert.ok(migrated1);
  assert.strictEqual(migrated1.farm_id, "farm-nalgonda-01");
  assert.strictEqual(migrated1.attachment_ids.length, 1);

  const migratedAttach = await OfflineDB.getAttachment(migrated1.attachment_ids[0]);
  assert.ok(migratedAttach);
  assert.strictEqual(migratedAttach.filename, "paddy_blast.jpg");
});

test("StorageMigration - migration is idempotent", async () => {
  // Already migrated in previous test
  assert.strictEqual(StorageMigration.isMigrationNeeded(), false);
  const result = await StorageMigration.migrateLegacyStorage();
  assert.strictEqual(result.migrated_count, 0);
  assert.strictEqual(result.success, true);
});

test("OfflineQueue - exponential backoff with jitter calculation", () => {
  const delay0 = OfflineQueue.calculateBackoffDelay(0);
  assert.ok(delay0 >= 1000 && delay0 <= 1500);

  const delay1 = OfflineQueue.calculateBackoffDelay(1);
  assert.ok(delay1 >= 2000 && delay1 <= 2500);

  const delay5 = OfflineQueue.calculateBackoffDelay(5);
  assert.ok(delay5 >= 30000 && delay5 <= 30500); // capped at 30s + jitter
});

test("OfflineQueue - handles 409 conflict preservation without data loss", async () => {
  await OfflineQueue.clear();

  const draft = OfflineQueue.saveDraft({
    type: "OBSERVATION",
    farm_id: "farm-conflict-01",
    notes: "Conflicting local observation",
  });

  const mockConflictApi = {
    createObservation: async () => {
      throw new Error("HTTP 409: Conflict - observation already exists on server");
    },
    uploadObservationMedia: async () => ({ id: "m-1" }),
    requestDiagnosis: async () => ({}),
  };

  const syncResult = await OfflineQueue.syncAll(mockConflictApi);
  assert.strictEqual(syncResult.conflicts, 1);
  assert.strictEqual(syncResult.synced, 0);

  const conflicts = await OfflineDB.getConflicts();
  assert.strictEqual(conflicts.length, 1);
  assert.strictEqual(conflicts[0].record_id, draft.id);
  assert.ok(conflicts[0].conflict_reason.includes("409"));
});

test("OfflineQueue - successful end-to-end sync cleans up synced records", async () => {
  await OfflineQueue.clear();

  const draft = OfflineQueue.saveDraft({
    type: "DIAGNOSIS_REQUEST",
    farm_id: "farm-warangal-success",
    crop_type: "cotton",
    notes: "Whitefly infestation",
  });

  let serverObservationCreated = false;
  let serverDiagnosisRequested = false;

  const mockSuccessApi = {
    createObservation: async (data) => {
      serverObservationCreated = true;
      assert.strictEqual(data.farm_id, "farm-warangal-success");
      assert.ok(data.idempotency_key);
      return { id: "server-obs-999" };
    },
    uploadObservationMedia: async () => ({ id: "media-999" }),
    requestDiagnosis: async (data) => {
      serverDiagnosisRequested = true;
      assert.strictEqual(data.crop_type, "cotton");
      return { status: "ACCEPTED" };
    },
  };

  const syncResult = await OfflineQueue.syncAll(mockSuccessApi);
  assert.strictEqual(syncResult.synced, 1);
  assert.strictEqual(syncResult.failed, 0);
  assert.strictEqual(serverObservationCreated, true);
  assert.strictEqual(serverDiagnosisRequested, true);

  // Record is removed from queue on completion
  assert.strictEqual(OfflineQueue.getDrafts().length, 0);
});
