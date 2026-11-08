# ACREVIA Participant Withdrawal & Data Erasure SOP
## Standard Operating Procedure for Voluntary Pilot Exit & Data Deletion
**Target Stage:** Stage 08 Remediation (`TASK-S08-01`)  
**Legal Framework:** Digital Personal Data Protection Act 2023 (Section 6(4) & Section 12)  
**Execution Timeframe:** Hard SLA of 72 hours from request receipt to complete data purge  

---

## 1. Principles of Voluntary Participation

Every participating farmer in the ACREVIA Telangana Field Pilot has an absolute, unalienable right to withdraw from the study at any point without explanation, coercion, economic penalty, or compromise of their relationship with the local KVK or agricultural extension services.

---

## 2. Channels for Requesting Withdrawal

A participant may exercise their right to withdraw through any of the following 3 mechanisms:

1. **In-App Self-Service:**
   Navigate to `Settings` $\to$ `Privacy & Consent` $\to$ Tap **"Withdraw Consent & Delete My Data (సమ్మతిని ఉపసంహరించుకోండి)"**.
2. **Field Assistant Direct Request:**
   Inform the Village Field Assistant verbally or in writing during village hours.
3. **Helpline / SMS:**
   Send an SMS or WhatsApp message stating `"WITHDRAW <Participant ID>"` to `+91 94400 12345`.

---

## 3. Four-Step Technical & Operational Execution SOP

```
[Step 1: Receipt & Verification] ──> [Step 2: Immediate Access Deactivation]
                                                     │
                                                     v
[Step 4: Confirmation & Closeout] <── [Step 3: Cascading 72-Hour Data Purge]
```

### Step 1: Verification & Identity Protection
- To protect farmers against malicious third-party tampering, a 4-digit SMS OTP is sent to the registered mobile number.
- Once confirmed by OTP or witnessed by the Village Field Assistant, the withdrawal ticket is logged with timestamp, reason (optional), and agent ID.

### Step 2: Immediate Account Deactivation (T + 0 Hours)
- The participant account is marked `is_active = False` in the database.
- Active JWT access tokens and refresh tokens are immediately blacklisted in Redis.
- Background sync from the participant's device is blocked from processing new entries.

### Step 3: Cascading Data Erasure Protocol (T + 1 to T + 72 Hours)
The automated data protection worker executes a secure cascading purge:

1. **Relational Database (`PostgreSQL`):**
   ```sql
   -- Purge user credentials and PII
   DELETE FROM users WHERE id = :participant_id;
   -- Purge associated farm profiles
   DELETE FROM farms WHERE user_id = :participant_id;
   -- Purge journal entries and scouting records
   DELETE FROM observations WHERE farm_id IN (:farm_ids);
   -- Log anonymized consent revocation event
   INSERT INTO consent_audit_log (event, timestamp, hash_id)
   VALUES ('CONSENT_REVOKED', NOW(), :sha256_hash);
   ```

2. **Object Storage (`AWS S3 / Storage Provider`):**
   - All uploaded leaf photos associated with the participant's observation records are permanently deleted using hard delete:
     `DELETE s3://acrevia-pilot/observations/<participant_id>/*`
   - Image thumbnails and intermediate image cache files are purged.

3. **Client-Side Purge (`IndexedDB`):**
   - On next app open, a server tombstone signal directs the client PWA to execute:
     ```javascript
     await indexedDB.deleteDatabase('acrevia_offline_db_v2');
     localStorage.clear();
     sessionStorage.clear();
     ```
   - All local drafts, binary blobs, and cached data are obliterated from the device.

### Step 4: Formal Written / SMS Confirmation (T + 72 Hours)
- An automated confirmation SMS in Telugu is dispatched to the farmer:
  *"మీ అభ్యర్థన మేరకు ఎక్రీవియా అధ్యయనం నుండి మీ వివరాలు మరియు ఫోటోలు పూర్తిగా తొలగించబడ్డాయి. ధన్యవాదాలు."*  
  *(As requested, your details and photos have been permanently removed from the ACREVIA study. Thank you.)*
- A physical confirmation receipt is placed in the project compliance folder by the DPO.

---

## 4. Treatment of Previously Anonymized Scientific Data

- In accordance with DPDP Act 2023 guidelines, statistical aggregations that were already fully anonymized prior to the withdrawal (e.g. "Total Warangal Cotton observations in Week 2 = 120") are retained for scientific reproducibility because they cannot be reverse-engineered to identify the individual.
- All raw images, identifiable coordinates, notes, and individual logs are 100% destroyed.
