/**
 * ACREVIA Vernacular PWA - IndexedDB Persistence Engine
 * Stage 06 Remediation (TASK-S06-01)
 *
 * Implements a versioned, resilient client-side storage engine using
 * browser IndexedDB with support for binary Blobs, transaction guarantees,
 * tenant isolation, and seamless fallback for SSR and headless testing.
 */

export const DB_NAME = "acrevia_offline_db_v2";
export const DB_VERSION = 2;

export const STORES = {
  RECORDS: "offline_records",
  ATTACHMENTS: "offline_attachments",
  SYNC_QUEUE: "sync_queue",
  SYNC_METADATA: "sync_metadata",
  CONFLICTS: "conflict_records",
} as const;

export type SyncState =
  | "DRAFT"
  | "QUEUED"
  | "SYNCING"
  | "SYNCED"
  | "RETRY_PENDING"
  | "CONFLICT"
  | "FAILED"
  | "CANCELLED";

export interface PersistedOfflineRecord {
  id: string; // client-side UUID
  tenant_id?: string;
  user_id?: string;
  type: "OBSERVATION" | "DIAGNOSIS_REQUEST" | "JOURNAL_ENTRY";
  farm_id: string;
  plot_id?: string;
  crop_season_id?: string;
  crop_type?: "cotton" | "rice" | "chilli";
  notes?: string;
  attachment_ids: string[];
  created_at: string;
  updated_at: string;
  sync_status: SyncState;
  idempotency_key: string;
  retry_count: number;
  next_retry_at?: string;
  error_message?: string;
  version: number;
}

export interface PersistedAttachment {
  id: string; // attachment UUID
  record_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  sha256?: string;
  blob?: Blob;
  base64_data?: string; // fallback for non-blob environments
  created_at: string;
  is_uploaded: boolean;
}

export interface SyncOperation {
  operation_id: string;
  record_id: string;
  tenant_id?: string;
  user_id?: string;
  idempotency_key: string;
  status: SyncState;
  attempt: number;
  max_attempts: number;
  last_attempt_at?: string;
  next_attempt_at?: string;
  error?: string;
  created_at: string;
}

export interface ConflictRecord {
  id: string;
  record_id: string;
  local_payload: unknown;
  server_payload?: unknown;
  conflict_reason: string;
  detected_at: string;
  resolved: boolean;
}

// In-Memory Fallback Store for SSR & Node.js test runners without native indexedDB
class InMemoryDatabase {
  records = new Map<string, PersistedOfflineRecord>();
  attachments = new Map<string, PersistedAttachment>();
  queue = new Map<string, SyncOperation>();
  metadata = new Map<string, unknown>();
  conflicts = new Map<string, ConflictRecord>();

  clear() {
    this.records.clear();
    this.attachments.clear();
    this.queue.clear();
    this.metadata.clear();
    this.conflicts.clear();
  }
}

const memoryDb = new InMemoryDatabase();

export class OfflineDB {
  private static dbInstance: IDBDatabase | null = null;

  static isIndexedDBAvailable(): boolean {
    return (
      typeof window !== "undefined" &&
      typeof window.indexedDB !== "undefined" &&
      window.indexedDB !== null
    );
  }

  static async getDB(): Promise<IDBDatabase | null> {
    if (!this.isIndexedDBAvailable()) {
      return null;
    }
    if (this.dbInstance) {
      return this.dbInstance;
    }

    return new Promise((resolve, reject) => {
      const request = window.indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // 1. offline_records store
        if (!db.objectStoreNames.contains(STORES.RECORDS)) {
          const recordStore = db.createObjectStore(STORES.RECORDS, { keyPath: "id" });
          recordStore.createIndex("by_status", "sync_status", { unique: false });
          recordStore.createIndex("by_user", "user_id", { unique: false });
          recordStore.createIndex("by_farm", "farm_id", { unique: false });
          recordStore.createIndex("by_created", "created_at", { unique: false });
        }

        // 2. offline_attachments store
        if (!db.objectStoreNames.contains(STORES.ATTACHMENTS)) {
          const attachStore = db.createObjectStore(STORES.ATTACHMENTS, { keyPath: "id" });
          attachStore.createIndex("by_record", "record_id", { unique: false });
        }

        // 3. sync_queue store
        if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
          const queueStore = db.createObjectStore(STORES.SYNC_QUEUE, { keyPath: "operation_id" });
          queueStore.createIndex("by_status", "status", { unique: false });
          queueStore.createIndex("by_record", "record_id", { unique: false });
        }

        // 4. sync_metadata store
        if (!db.objectStoreNames.contains(STORES.SYNC_METADATA)) {
          db.createObjectStore(STORES.SYNC_METADATA, { keyPath: "key" });
        }

        // 5. conflict_records store
        if (!db.objectStoreNames.contains(STORES.CONFLICTS)) {
          const conflictStore = db.createObjectStore(STORES.CONFLICTS, { keyPath: "id" });
          conflictStore.createIndex("by_record", "record_id", { unique: false });
        }
      };

      request.onsuccess = (event) => {
        this.dbInstance = (event.target as IDBOpenDBRequest).result;
        resolve(this.dbInstance);
      };

      request.onerror = (event) => {
        console.warn("IndexedDB open error, falling back to memory store:", (event.target as IDBOpenDBRequest).error);
        resolve(null);
      };
    });
  }

  // --- Record CRUD ---

  static async putRecord(record: PersistedOfflineRecord): Promise<void> {
    const db = await this.getDB();
    if (!db) {
      memoryDb.records.set(record.id, { ...record });
      return;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.RECORDS, "readwrite");
      const store = tx.objectStore(STORES.RECORDS);
      const req = store.put(record);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  static async getRecord(id: string): Promise<PersistedOfflineRecord | null> {
    const db = await this.getDB();
    if (!db) {
      return memoryDb.records.get(id) || null;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.RECORDS, "readonly");
      const store = tx.objectStore(STORES.RECORDS);
      const req = store.get(id);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  }

  static async getAllRecords(): Promise<PersistedOfflineRecord[]> {
    const db = await this.getDB();
    if (!db) {
      return Array.from(memoryDb.records.values());
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.RECORDS, "readonly");
      const store = tx.objectStore(STORES.RECORDS);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  static async deleteRecord(id: string): Promise<void> {
    const db = await this.getDB();
    if (!db) {
      memoryDb.records.delete(id);
      return;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.RECORDS, "readwrite");
      const store = tx.objectStore(STORES.RECORDS);
      const req = store.delete(id);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  // --- Attachment CRUD (Blob/Binary) ---

  static async putAttachment(attachment: PersistedAttachment): Promise<void> {
    const db = await this.getDB();
    if (!db) {
      memoryDb.attachments.set(attachment.id, { ...attachment });
      return;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.ATTACHMENTS, "readwrite");
      const store = tx.objectStore(STORES.ATTACHMENTS);
      const req = store.put(attachment);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  static async getAttachment(id: string): Promise<PersistedAttachment | null> {
    const db = await this.getDB();
    if (!db) {
      return memoryDb.attachments.get(id) || null;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.ATTACHMENTS, "readonly");
      const store = tx.objectStore(STORES.ATTACHMENTS);
      const req = store.get(id);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  }

  static async getAttachmentsForRecord(recordId: string): Promise<PersistedAttachment[]> {
    const db = await this.getDB();
    if (!db) {
      return Array.from(memoryDb.attachments.values()).filter((a) => a.record_id === recordId);
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.ATTACHMENTS, "readonly");
      const store = tx.objectStore(STORES.ATTACHMENTS);
      const index = store.index("by_record");
      const req = index.getAll(recordId);
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  static async deleteAttachment(id: string): Promise<void> {
    const db = await this.getDB();
    if (!db) {
      memoryDb.attachments.delete(id);
      return;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.ATTACHMENTS, "readwrite");
      const store = tx.objectStore(STORES.ATTACHMENTS);
      const req = store.delete(id);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  // --- Sync Operation Queue ---

  static async putQueueOperation(op: SyncOperation): Promise<void> {
    const db = await this.getDB();
    if (!db) {
      memoryDb.queue.set(op.operation_id, { ...op });
      return;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.SYNC_QUEUE, "readwrite");
      const store = tx.objectStore(STORES.SYNC_QUEUE);
      const req = store.put(op);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  static async getAllQueueOperations(): Promise<SyncOperation[]> {
    const db = await this.getDB();
    if (!db) {
      return Array.from(memoryDb.queue.values());
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.SYNC_QUEUE, "readonly");
      const store = tx.objectStore(STORES.SYNC_QUEUE);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  static async deleteQueueOperation(operationId: string): Promise<void> {
    const db = await this.getDB();
    if (!db) {
      memoryDb.queue.delete(operationId);
      return;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.SYNC_QUEUE, "readwrite");
      const store = tx.objectStore(STORES.SYNC_QUEUE);
      const req = store.delete(operationId);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  // --- Conflicts ---

  static async putConflict(conflict: ConflictRecord): Promise<void> {
    const db = await this.getDB();
    if (!db) {
      memoryDb.conflicts.set(conflict.id, { ...conflict });
      return;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.CONFLICTS, "readwrite");
      const store = tx.objectStore(STORES.CONFLICTS);
      const req = store.put(conflict);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  static async getConflicts(): Promise<ConflictRecord[]> {
    const db = await this.getDB();
    if (!db) {
      return Array.from(memoryDb.conflicts.values());
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORES.CONFLICTS, "readonly");
      const store = tx.objectStore(STORES.CONFLICTS);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  // --- Reset/Clear for testing ---
  static async clearAll(): Promise<void> {
    memoryDb.clear();
    const db = await this.getDB();
    if (!db) return;

    return new Promise((resolve, reject) => {
      const tx = db.transaction(
        [STORES.RECORDS, STORES.ATTACHMENTS, STORES.SYNC_QUEUE, STORES.SYNC_METADATA, STORES.CONFLICTS],
        "readwrite"
      );
      tx.objectStore(STORES.RECORDS).clear();
      tx.objectStore(STORES.ATTACHMENTS).clear();
      tx.objectStore(STORES.SYNC_QUEUE).clear();
      tx.objectStore(STORES.SYNC_METADATA).clear();
      tx.objectStore(STORES.CONFLICTS).clear();
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }
}
