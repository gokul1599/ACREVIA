export interface OfflineDraft {
  id: string; // client-side UUID
  type: "OBSERVATION" | "DIAGNOSIS_REQUEST";
  farm_id: string;
  plot_id?: string;
  crop_season_id?: string;
  crop_type?: "cotton" | "rice" | "chilli";
  notes?: string;
  image_data_base64?: string; // base64 representation for offline storage
  image_filename?: string;
  created_at: string;
  sync_status: "PENDING" | "SYNCING" | "FAILED";
  error_message?: string;
}

const STORAGE_KEY = "acrevia_offline_drafts_v1";

export class OfflineQueue {
  static getDrafts(): OfflineDraft[] {
    if (typeof window === "undefined") return [];
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  static saveDraft(draft: Omit<OfflineDraft, "id" | "created_at" | "sync_status">): OfflineDraft {
    const drafts = this.getDrafts();
    const newDraft: OfflineDraft = {
      ...draft,
      id: "draft-" + Date.now() + "-" + Math.random().toString(36).substring(2, 9),
      created_at: new Date().toISOString(),
      sync_status: "PENDING",
    };
    drafts.push(newDraft);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
      } catch (err) {
        console.warn("Storage quota exceeded for offline drafts", err);
      }
    }
    return newDraft;
  }

  static removeDraft(id: string) {
    const drafts = this.getDrafts().filter((d) => d.id !== id);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
      } catch {
        // ignore
      }
    }
  }

  static updateDraftStatus(id: string, status: "PENDING" | "SYNCING" | "FAILED", error?: string) {
    const drafts = this.getDrafts().map((d) => {
      if (d.id === id) {
        return { ...d, sync_status: status, error_message: error };
      }
      return d;
    });
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
      } catch {
        // ignore
      }
    }
  }

  static async syncAll(apiClient: typeof import("@/lib/api/client").api): Promise<{
    synced: number;
    failed: number;
  }> {
    const drafts = this.getDrafts().filter((d) => d.sync_status === "PENDING" || d.sync_status === "FAILED");
    let synced = 0;
    let failed = 0;

    for (const draft of drafts) {
      this.updateDraftStatus(draft.id, "SYNCING");
      try {
        // 1. Create server-side observation
        const obs = await apiClient.createObservation({
          farm_id: draft.farm_id,
          plot_id: draft.plot_id,
          crop_season_id: draft.crop_season_id,
          notes: draft.notes ? `[Offline Synced] ${draft.notes}` : "[Offline Synced Observation]",
        });

        // 2. Upload photo if present
        let mediaId: string | undefined;
        if (draft.image_data_base64) {
          const res = await fetch(draft.image_data_base64);
          const blob = await res.blob();
          const media = await apiClient.uploadObservationMedia(
            obs.id,
            blob,
            draft.image_filename || "foliar.jpg",
            true
          );
          mediaId = media.id;
        }

        // 3. Request diagnosis if this was a diagnosis draft
        if (draft.type === "DIAGNOSIS_REQUEST" && draft.crop_type) {
          await apiClient.requestDiagnosis({
            observation_id: obs.id,
            media_id: mediaId,
            crop_type: draft.crop_type,
          });
        }

        this.removeDraft(draft.id);
        synced++;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Sync failed";
        this.updateDraftStatus(draft.id, "FAILED", msg);
        failed++;
      }
    }

    return { synced, failed };
  }
}
