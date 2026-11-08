# ACREVIA — AUTHENTICATION AND AUTHORIZATION SPECIFICATION
## Cryptographic Security, JWT Lifecycle, Dual-Tier RBAC, and Multi-Tenant Isolation

---

## 1. Authentication Architecture & Token Lifecycle

ACREVIA uses JSON Web Tokens (JWT) adhering to RFC 7519, signed using HMAC-SHA256 (`HS256`) with a cryptographically secure 256-bit secret key.

### Token Claims Structure:
- `sub`: Unique User UUID string (`user.id`).
- `roles`: List of assigned system roles (`["FARMER"]`, `["AGRICULTURAL_EXPERT"]`, `["ADMIN"]`).
- `iss`: Canonical issuer (`acrevia-auth-service`).
- `iat`: Timestamp issued at (UTC epoch seconds).
- `exp`: Timestamp expires at (UTC epoch seconds). Default access token lifespan: **1440 minutes (24 hours)**.

### Password Storage Security:
- All passwords are encrypted using **bcrypt** with a cost factor (work factor) of **12 rounds**, resisting offline rainbow-table and GPU brute-force attacks.
- Passwords must meet minimum complexity constraints: at least 8 characters, with a maximum length of 128 characters to prevent algorithmic Denial of Service (DoS).

---

## 2. Dual-Tier Authorization Model

ACREVIA implements a two-tier permission model that decouples platform-wide capabilities from farm-level resource ownership:

```
+---------------------------------------------------------------------------------------+
|                                    TIER 1: SYSTEM ROLES                               |
|                     (Determines global application privileges)                        |
|                                                                                       |
|  - FARMER: Core agricultural user managing personal farms, observations & diagnoses. |
|  - AGRICULTURAL_EXPERT: Certified agronomist authorized to submit expert reviews.     |
|  - RESEARCHER: Read-only access to anonymized epidemiological & pathology patterns.   |
|  - ADMIN: Platform operations, user verification, and emergency cross-farm review.    |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                                  TIER 2: FARM ROLES                                   |
|                (Determines permissions within a specific farm holding)                |
|                                                                                       |
|  - OWNER: Full control over farm metadata, plot configuration, and member management. |
|  - MANAGER: Can add plots, record crop seasons, and upload observations.              |
|  - WORKER: Can upload observations and scouting media; cannot modify farm boundaries. |
|  - AGRONOMIST_ADVISOR: Assigned consultant with read access to plot history & reports.|
+---------------------------------------------------------------------------------------+
```

---

## 3. Multi-Tenant Isolation Enforcement (`verify_farm_access`)

Tenant boundaries are strictly checked at the FastAPI dependency and service layer before any database query or mutation executes:

```python
def verify_farm_access(farm_id: str, user: User, db: Session, allowed_farm_roles=None) -> Farm:
    # 1. Superuser override (ADMIN system role)
    if SystemRole.ADMIN.value in [r.id for r in user.roles]:
        return farm

    # 2. Primary Owner check
    if farm.owner_id == user.id:
        return farm

    # 3. Collaborative Membership check
    membership = db.query(FarmMembership).filter_by(farm_id=farm_id, user_id=user.id).first()
    if membership:
        if allowed_farm_roles and membership.role_in_farm not in allowed_farm_roles:
            raise HTTPException(status_code=403, detail="Insufficient farm role.")
        return farm

    # 4. Cross-Tenant Attempt: Blocked with HTTP 403 Forbidden
    raise HTTPException(status_code=403, detail="Access to requested farm is forbidden.")
```

### Verified Security Guarantees:
- **No Inadvertent Cross-Tenant Leaks:** A user cannot view, list, or download foliar photographs belonging to an unassigned farm.
- **Fail-Closed Default:** If a farm identifier does not exist or has been archived, the system returns `404 Not Found`. If a user lacks membership, the system returns `403 Forbidden`.
