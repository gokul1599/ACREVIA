# ACREVIA Stage 14 — Data Exchange & Portability Model

## 1. Supported Formats & Manifest Specification
ACREVIA Exchange provides bidirectional data interchange supporting 4 serialization formats:
1. **Canonical JSON Package:** Standard JSON object containing schema version, timestamp, tenant ID, and grouped entities.
2. **Flattened CSV Table:** Multi-category CSV stream suitable for spreadsheet analysis.
3. **Spatial GeoJSON:** RFC-7946 FeatureCollection encoding plot boundaries and farm centroids.
4. **Cryptographic ZIP Archive:** Multi-file archive bundling category JSON files and a cryptographic `MANIFEST.json`.

### Cryptographic Manifest Structure (`MANIFEST.json`):
```json
{
  "package_id": "8a31b412-f489-4a11-c87d-000000000001",
  "exported_at": "2026-11-08T13:30:00Z",
  "tenant_id": "user-uuid",
  "checksum_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
  "entity_counts": {
    "farms": 1,
    "soil_samples": 4,
    "observations": 12,
    "expenses": 8
  },
  "canonical_units": {
    "mass": "kg / quintal",
    "area": "acre / ha"
  }
}
```

---

## 2. Safe Import & Non-Overwriting Conflict Guarantee
When agricultural data is imported:
1. Columns are mapped to canonical names using optional `DataMappingProfile`.
2. Records are validated against the canonical data dictionary.
3. **If a conflicting record is identified** (matching ID, sample code, or timestamp for that plot), the existing database record is **never overwritten**.
4. Both records are preserved, the imported entity is flagged with a conflict marker (e.g. `TS-WAR-001_CONFLICT_20261108`), and `conflicts_detected` is incremented for explicit human verification.
