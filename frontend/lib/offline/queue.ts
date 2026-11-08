/**
 * ACREVIA Vernacular PWA - Resilient Offline Synchronization Queue
 * Stage 06 Remediation (TASK-S06-01)
 *
 * Implements high-capacity IndexedDB persistence with support for binary
 * image Blobs, idempotent synchronization, exponential backoff with jitter,
 * conflict preservation, account tenancy, and backwards compatibility.
 */

import { OfflineDB } from "./db.ts";
import type { PersistedOfflineRecord, PersistedAttachment, SyncState, ConflictRecord } from "./db.ts";
import { StorageMigration } from "./migration.ts";

export interface OfflineDraft {
  id: string; // client-side UUID
  tenant_id?: string;
  user_id?: string;
  type: "OBSERVATION" | "DIAGNOSIS_REQUEST" | "JOURNAL_ENTRY";
  farm_id: string;
  plot_id?: string;
  crop_season_id?: string;
  crop_type?: "cotton" | "rice" | "chilli";
  notes?: string;
  image_data_base64?: string; // legacy base64 support
  image_blob?: Blob; // binary blob support
  image_filename?: string;
  attachment_ids?: string[];
  created_at: string;
  updated_at?: string;
  sync_status: SyncState | "PENDING" | "SYNCING" | "FAILED";
  idempotency_key?: string;
  error_message?: string;
}

const STORAGE_KEY = "acrevia_offline_drafts_v1";

// In-memory cache for synchronous compatibility
let inMemoryCache: OfflineDraft[] = [];
let isCacheLoaded = false;

export class OfflineQueue {
  private static syncWithLocalStorage(): void {
    if (typeof window !== "undefined" && typeof localStorage !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(inMemoryCache));
      } catch (err) {
        // Quota exceeded in localStorage is gracefully handled
        console.warn("localStorage quota exceeded, retaining full payload in IndexedDB:", err);
      }
    }
  }

  private static reloadFromLocalStorageIfNeeded(): void {
    if (typeof window !== "undefined" && typeof localStorage !== "undefined") {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) {
          // localStorage was cleared (e.g., in a test environment or user storage clear)
          inMemoryCache = [];
          return;
        }
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          inMemoryCache = parsed;
        }
      } catch {
        // ignore JSON errors
      }
    }
  }

  private static async ensureLoaded(): Promise<void> {
    if (isCacheLoaded) return;

    // Check if migration is needed
    if (StorageMigration.isMigrationNeeded()) {
      await StorageMigration.migrateLegacyStorage();
    }

    const records = await OfflineDB.getAllRecords();
    if (records.length > 0) {
      inMemoryCache = records.map((r) => ({
        id: r.id,
        tenant_id: r.tenant_id,
        user_id: r.user_id,
        type: r.type,
        farm_id: r.farm_id,
        plot_id: r.plot_id,
        crop_season_id: r.crop_season_id,
        crop_type: r.crop_type,
        notes: r.notes,
        attachment_ids: r.attachment_ids,
        created_at: r.created_at,
        updated_at: r.updated_at,
        sync_status: r.sync_status,
        idempotency_key: r.idempotency_key,
        error_message: r.error_message,
      }));
    } else {
      this.reloadFromLocalStorageIfNeeded();
    }
    isCacheLoaded = true;
  }

  // --- Synchronous Backwards Compatible API ---

  static getDrafts(): OfflineDraft[] {
    if (typeof window !== "undefined") {
      this.reloadFromLocalStorageIfNeeded();
    }
    return [...inMemoryCache];
  }

  static saveDraft(
    draft: Omit<OfflineDraft, "id" | "created_at" | "sync_status"> & {
      id?: string;
      image_blob?: Blob;
    }
  ): OfflineDraft {
    this.reloadFromLocalStorageIfNeeded();

    const id = draft.id || "draft-" + Date.now() + "-" + Math.random().toString(36).substring(2, 9);
    const now = new Date().toISOString();
    const idempotencyKey = `idemp-${id}`;

    const attachmentIds: string[] = draft.attachment_ids ? [...draft.attachment_ids] : [];

    // Persist attachment asynchronously if present
    if (draft.image_blob || draft.image_data_base64) {
      const attachId = `attach-${id}-${Date.now()}`;
      attachmentIds.push(attachId);

      const attachment: PersistedAttachment = {
        id: attachId,
        record_id: id,
        filename: draft.image_filename || "foliar.jpg",
        mime_type: draft.image_blob?.type || "image/jpeg",
        size_bytes: draft.image_blob ? draft.image_blob.size : Math.round(((draft.image_data_base64?.length || 0) * 3) / 4),
        blob: draft.image_blob,
        base64_data: draft.image_data_base64,
        created_at: now,
        is_uploaded: false,
      };

      OfflineDB.putAttachment(attachment).catch((err) => {
        console.warn("Failed to persist attachment to IndexedDB:", err);
      });
    }

    const newDraft: OfflineDraft = {
      ...draft,
      id,
      attachment_ids: attachmentIds,
      created_at: now,
      updated_at: now,
      sync_status: "PENDING",
      idempotency_key: idempotencyKey,
    };

    inMemoryCache.push(newDraft);
    this.syncWithLocalStorage();

    // Persist record to IndexedDB
    const record: PersistedOfflineRecord = {
      id: newDraft.id,
      tenant_id: newDraft.tenant_id,
      user_id: newDraft.user_id,
      type: newDraft.type,
      farm_id: newDraft.farm_id,
      plot_id: newDraft.plot_id,
      crop_season_id: newDraft.crop_season_id,
      crop_type: newDraft.crop_type,
      notes: newDraft.notes,
      attachment_ids: attachmentIds,
      created_at: now,
      updated_at: now,
      sync_status: "QUEUED",
      idempotency_key: idempotencyKey,
      retry_count: 0,
      version: 1,
    };

    OfflineDB.putRecord(record).catch((err) => {
      console.warn("Storage error saving offline draft to IndexedDB:", err);
    });

    return newDraft;
  }

  static removeDraft(id: string) {
    this.reloadFromLocalStorageIfNeeded();
    inMemoryCache = inMemoryCache.filter((d) => d.id !== id);
    this.syncWithLocalStorage();

    // Asynchronously delete record and associated attachments
    OfflineDB.deleteRecord(id).catch(console.error);
    OfflineDB.getAttachmentsForRecord(id).then((attachments) => {
      for (const a of attachments) {
        OfflineDB.deleteAttachment(a.id).catch(console.error);
      }
    }).catch(console.error);
  }

  static updateDraftStatus(
    id: string,
    status: SyncState | "PENDING" | "SYNCING" | "FAILED",
    error?: string
  ) {
    this.reloadFromLocalStorageIfNeeded();
    inMemoryCache = inMemoryCache.map((d) => {
      if (d.id === id) {
        return {
          ...d,
          sync_status: status,
          error_message: error,
          updated_at: new Date().toISOString(),
        };
      }
      return d;
    });
    this.syncWithLocalStorage();

    OfflineDB.getRecord(id).then((record) => {
      if (record) {
        record.sync_status = status as SyncState;
        record.error_message = error;
        record.updated_at = new Date().toISOString();
        if (status === "FAILED") {
          record.retry_count += 1;
        }
        OfflineDB.putRecord(record).catch(console.error);
      }
    }).catch(console.error);
  }

  // --- Asynchronous IndexedDB Operations ---

  static async loadAllRecords(): Promise<PersistedOfflineRecord[]> {
    await this.ensureLoaded();
    return OfflineDB.getAllRecords();
  }

  static async getRecordAttachments(recordId: string): Promise<PersistedAttachment[]> {
    return OfflineDB.getAttachmentsForRecord(recordId);
  }

  // --- Exponential Backoff & Jitter ---
  static calculateBackoffDelay(retryCount: number): number {
    const baseDelayMs = 1000;
    const maxDelayMs = 30000;
    const exponential = Math.min(maxDelayMs, baseDelayMs * Math.pow(2, retryCount));
    const jitter = Math.random() * 500;
    return exponential + jitter;
  }

  // --- Synchronize All (IndexedDB + API Client) ---
  static async syncAll(apiClient: {
    createObservation: (data: {
      farm_id: string;
      plot_id?: string;
      crop_season_id?: string;
      notes?: string;
      symptom_tags?: string;
      client_id?: string;
      idempotency_key?: string;
    }) => Promise<{ id: string }>;
    uploadObservationMedia: (obsId: string, blob: Blob, filename: string, isPrimary: boolean) => Promise<{ id: string }>;
    requestDiagnosis: (data: {
      observation_id: string;
      media_id?: string;
      crop_type: "cotton" | "rice" | "chilli";
    }) => Promise<unknown>;
  }): Promise<{
    synced: number;
    failed: number;
    conflicts: number;
  }> {
    await this.ensureLoaded();
    const records = await OfflineDB.getAllRecords();
    const pendingRecords = records.filter(
      (r) => r.sync_status === "QUEUED" || r.sync_status === "RETRY_PENDING" || (r.sync_status as string) === "PENDING" || (r.sync_status as string) === "FAILED"
    );

    let synced = 0;
    let failed = 0;
    let conflicts = 0;

    for (const record of pendingRecords) {
      this.updateDraftStatus(record.id, "SYNCING");

      try {
        // 1. Create server observation with idempotency metadata
        const obs = await apiClient.createObservation({
          farm_id: record.farm_id,
          plot_id: record.plot_id,
          crop_season_id: record.crop_season_id,
          client_id: record.id,
          idempotency_key: record.idempotency_key,
          notes: record.notes ? `[Offline Synced] ${record.notes}` : "[Offline Synced Observation]",
        });

        // 2. Fetch binary attachments from IndexedDB
        const attachments = await OfflineDB.getAttachmentsForRecord(record.id);
        let primaryMediaId: string | undefined;

        for (const attach of attachments) {
          let blobToUpload = attach.blob;
          if (!blobToUpload && attach.base64_data) {
            const res = await fetch(attach.base64_data);
            blobToUpload = await res.blob();
          }

          if (blobToUpload) {
            const media = await apiClient.uploadObservationMedia(
              obs.id,
              blobToUpload,
              attach.filename || "foliar.jpg",
              true
            );
            primaryMediaId = media.id;
            attach.is_uploaded = true;
            await OfflineDB.putAttachment(attach);
          }
        }

        // 3. Trigger crop vision diagnosis if requested
        if (record.type === "DIAGNOSIS_REQUEST" && record.crop_type) {
          await apiClient.requestDiagnosis({
            observation_id: obs.id,
            media_id: primaryMediaId,
            crop_type: record.crop_type,
          });
        }

        // 4. Mark completed and clean up
        this.removeDraft(record.id);
        synced++;
      } catch (err: unknown) {
        const errorMsg = err instanceof Error ? err.message : "Sync failed";

        // Check for conflict response (e.g. 409 or conflict payload)
        if (errorMsg.includes("409") || errorMsg.toLowerCase().includes("conflict")) {
          conflicts++;
          const conflict: ConflictRecord = {
            id: `conflict-${record.id}-${Date.now()}`,
            record_id: record.id,
            local_payload: record,
            conflict_reason: errorMsg,
            detected_at: new Date().toISOString(),
            resolved: false,
          };
          await OfflineDB.putConflict(conflict);
          this.updateDraftStatus(record.id, "CONFLICT", errorMsg);
        } else {
          failed++;
          this.updateDraftStatus(record.id, "FAILED", errorMsg);
        }
      }
    }

    return { synced, failed, conflicts };
  }

  // Clear all drafts and attachments (testing and logout)
  static async clear(): Promise<void> {
    inMemoryCache = [];
    isCacheLoaded = true;
    if (typeof window !== "undefined" && typeof localStorage !== "undefined") {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch {
        // ignore
      }
    }
    await OfflineDB.clearAll();
  }
}
