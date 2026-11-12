"""
ACREVIA - Stage 12 Automated Test Suite.
Validates Agricultural Collaboration Network, Farmer Collectives, Knowledge Commons,
Research Hub & Data Governance, Extension Learning, and Regional Pulse Intelligence.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.user import User
from backend.app.models.knowledge_document import KnowledgeDocument


def test_scenario_a_acrevia_connect(
    client: TestClient,
    farmer_user: User,
    farmer_token: str,
    expert_user: User,
    expert_token: str,
):
    """Scenario A: Moderated community network, expert reply badges, helpful voting, and moderation reporting."""
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    expert_headers = {"Authorization": f"Bearer {expert_token}"}

    # 1. List communities and verify default seeded communities
    res_comms = client.get("/api/v1/connect/communities", headers=farmer_headers)
    assert res_comms.status_code == 200
    communities = res_comms.json()
    assert len(communities) >= 3
    cotton_comm = next((c for c in communities if c["slug"] == "cotton-telangana"), communities[0])

    # 2. Farmer joins the community
    res_join = client.post(f"/api/v1/connect/communities/{cotton_comm['id']}/join", headers=farmer_headers)
    assert res_join.status_code == 200
    assert res_join.json()["community_id"] == cotton_comm["id"]

    # 3. Farmer creates a discussion post
    post_payload = {
        "post_type": "FIELD_EXPERIENCE",
        "title": "Intercropping Cowpea in Cotton for Natural Predator Conservation",
        "content": "Observed significant reduction in early sucking pests by planting 1 row of cowpea every 8 rows of cotton in Warangal.",
        "language": "en",
        "crop_id": "cotton",
        "growth_stage": "VEGETATIVE",
        "visibility": "COMMUNITY_PUBLIC",
    }
    res_post = client.post(
        f"/api/v1/connect/communities/{cotton_comm['id']}/posts",
        json=post_payload,
        headers=farmer_headers,
    )
    assert res_post.status_code == 201
    post_data = res_post.json()
    post_id = post_data["id"]
    assert post_data["title"] == post_payload["title"]
    assert post_data["helpful_count"] == 0

    # 4. Verified Agronomist adds a reply comment (is_expert_reply should be True)
    expert_comment_payload = {
        "content": "Excellent field practice. Vigna unguiculata acts as a proven attractant for coccinellid predators.",
    }
    res_comm = client.post(
        f"/api/v1/connect/posts/{post_id}/comments",
        json=expert_comment_payload,
        headers=expert_headers,
    )
    assert res_comm.status_code == 201
    comment_data = res_comm.json()
    assert comment_data["is_expert_reply"] is True

    # 5. Non-expert farmer adds a reply (is_expert_reply should be False)
    farmer_comment_payload = {
        "content": "Does cowpea compete for water in red chalka soils?",
    }
    res_fcomm = client.post(
        f"/api/v1/connect/posts/{post_id}/comments",
        json=farmer_comment_payload,
        headers=farmer_headers,
    )
    assert res_fcomm.status_code == 201
    assert res_fcomm.json()["is_expert_reply"] is False

    # 6. Helpful vote recorded with scientific disclaimer
    res_vote = client.post(f"/api/v1/connect/posts/{post_id}/helpful", headers=farmer_headers)
    assert res_vote.status_code == 200
    vote_data = res_vote.json()
    assert vote_data["helpful_count"] == 1
    assert "scientific agronomic validation" in vote_data["message"]

    # 7. Misinformation reporting
    report_payload = {
        "post_id": post_id,
        "reason_category": "MISINFORMATION",
        "details": "Routine test report to verify moderation queue routing.",
    }
    res_rep = client.post("/api/v1/connect/report", json=report_payload, headers=farmer_headers)
    assert res_rep.status_code == 201
    assert res_rep.json()["status"] == "PENDING"


def test_scenario_b_acrevia_commons_governance(
    client: TestClient,
    farmer_user: User,
    farmer_token: str,
    expert_user: User,
    expert_token: str,
    admin_token: str,
    db_session: Session,
):
    """Scenario B: Governed knowledge contribution lifecycle, expert review, translation, and KrishiBrain handoff."""
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    expert_headers = {"Authorization": f"Bearer {expert_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Farmer/Agronomist submits a knowledge contribution
    contrib_payload = {
        "contribution_type": "EXPERT_ARTICLE",
        "title": "Sub-surface drip irrigation spacing and fertigation schedule for cotton in Telangana Vertisols",
        "description": "Lateral spacing of 1.5m with 0.4m dripper spacing delivers 35% water savings compared to flood irrigation in deep black soils.",
        "original_language": "en",
        "crop_id": "cotton",
        "geographic_scope": "Telangana Vertisols",
        "growth_stage": "BOLL_DEVELOPMENT",
        "evidence_references": [
            "PJTSAU Package of Practices 2024",
            "ICAR-CICR Cotton Technical Bulletin No. 42",
        ],
        "usage_permission": "CC_BY_SA_4_0",
    }
    res_sub = client.post("/api/v1/commons/contributions", json=contrib_payload, headers=farmer_headers)
    assert res_sub.status_code == 201
    contrib = res_sub.json()
    contrib_id = contrib["id"]
    assert contrib["status"] == "SUBMITTED"
    assert contrib["krishi_brain_ingested"] is False

    # 2. Unauthorized farmer attempt to review contribution must be rejected (403)
    farmer_review_payload = {
        "decision": "APPROVE",
        "comments": "Farmer attempting to review own knowledge",
        "scientific_rating": 5,
    }
    res_bad_review = client.post(
        f"/api/v1/commons/contributions/{contrib_id}/review",
        json=farmer_review_payload,
        headers=farmer_headers,
    )
    assert res_bad_review.status_code == 403

    # 3. Verified agricultural expert reviews and approves the contribution
    expert_review_payload = {
        "decision": "APPROVE",
        "comments": "Scientifically consistent with PJTSAU recommendation. Evidence references verified.",
        "scientific_rating": 5,
        "safety_assessment": "Safe for Telangana vertisols; avoid on poorly drained saline patches.",
    }
    res_rev = client.post(
        f"/api/v1/commons/contributions/{contrib_id}/review",
        json=expert_review_payload,
        headers=expert_headers,
    )
    assert res_rev.status_code == 201
    assert res_rev.json()["decision"] == "APPROVE"

    # Verify status changed to APPROVED
    res_get = client.get(f"/api/v1/commons/contributions/{contrib_id}", headers=farmer_headers)
    assert res_get.status_code == 200
    assert res_get.json()["status"] == "APPROVED"

    # 4. Add a Telugu translation version
    trans_payload = {
        "target_language": "te",
        "translated_title": "తెలంగాణ నల్లరేగడి నేలల్లో పత్తికి భూగర్భ బిందు సేద్యం విధానం",
        "translated_content": "1.5 మీటర్ల లాటరల్ మరియు 40 సెం.మీ డ్రిప్పర్ దూరం పాటించడం వల్ల 35% నీరు ఆదా అవుతుంది.",
    }
    res_trans = client.post(
        f"/api/v1/commons/contributions/{contrib_id}/translations",
        json=trans_payload,
        headers=farmer_headers,
    )
    assert res_trans.status_code == 201
    assert res_trans.json()["target_language"] == "te"

    # 5. Handoff to KrishiBrain RAG by admin
    res_handoff = client.post(
        f"/api/v1/commons/contributions/{contrib_id}/handoff-krishibrain",
        headers=admin_headers,
    )
    assert res_handoff.status_code == 200
    handoff_data = res_handoff.json()
    assert handoff_data["krishi_brain_ingested"] is True
    assert handoff_data["status"] == "PUBLISHED"
    assert handoff_data["krishi_brain_doc_id"] is not None

    # Verify KnowledgeDocument exists in database
    doc = db_session.get(KnowledgeDocument, handoff_data["krishi_brain_doc_id"])
    assert doc is not None
    assert "ACREVIA Commons" in doc.title


def test_scenario_c_acrevia_collectives_privacy_guardrail(
    client: TestClient,
    farmer_user: User,
    farmer_token: str,
    second_farmer_user: User,
    second_farmer_token: str,
    admin_token: str,
    db_session: Session,
):
    """Scenario C: FPO registration, verification, activities, and minimum cohort size rule (N >= 5)."""
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Register a Farmer Collective / FPO
    fpo_payload = {
        "name": "Warangal Organic Cotton Growers Cooperative",
        "org_type": "FPO",
        "registration_number": "FPO-TEL-2026-088",
        "state": "Telangana",
        "district": "Warangal",
        "description": "Federation of smallholder cotton and chilli farmers committed to IPM.",
        "contact_email": "coop@warangal-agro.org",
        "contact_phone": "+919876543210",
    }
    res_fpo = client.post("/api/v1/collectives/organizations", json=fpo_payload, headers=farmer_headers)
    assert res_fpo.status_code == 201
    org = res_fpo.json()
    org_id = org["id"]
    assert org["verification_status"] == "APPLICATION_SUBMITTED"

    # 2. Admin verifies the organization
    res_verify = client.post(f"/api/v1/collectives/organizations/{org_id}/verify?approve=true", headers=admin_headers)
    assert res_verify.status_code == 200
    assert res_verify.json()["verification_status"] == "APPROVED"

    # 3. Second farmer joins the collective
    second_headers = {"Authorization": f"Bearer {second_farmer_token}"}
    res_join = client.post(f"/api/v1/collectives/organizations/{org_id}/join?role=MEMBER", headers=second_headers)
    assert res_join.status_code == 200

    # 4. Schedule a collective activity
    target_date = (date.today() + timedelta(days=7)).isoformat()
    activity_payload = {
        "activity_type": "TRAINING_SESSION",
        "title": "Bio-fertilizer Inoculation Workshop",
        "description": "Hands-on demonstration of Rhizobium and PSB liquid seed treatment.",
        "target_date": target_date,
    }
    res_act = client.post(f"/api/v1/collectives/organizations/{org_id}/activities", json=activity_payload, headers=farmer_headers)
    assert res_act.status_code == 201
    assert res_act.json()["title"] == activity_payload["title"]

    # 5. Query aggregate analytics with INSUFFICIENT cohort (< 5 farms)
    res_analytics_small = client.get(f"/api/v1/collectives/organizations/{org_id}/analytics", headers=farmer_headers)
    assert res_analytics_small.status_code == 200
    small_analytics = res_analytics_small.json()
    assert small_analytics["privacy_cohort_status"] == "SUPPRESSED_INSUFFICIENT_COHORT"
    assert small_analytics["aggregated_acreage"] == 0.0
    assert len(small_analytics["crop_distribution"]) == 0
    assert "suppressed" in small_analytics["notes"].lower()

    # 6. Add dummy member farms to cross the N >= 5 threshold and verify analytics release
    # Create 4 additional members and farms
    for i in range(4):
        dummy_user = User(
            email=f"fpo_member_{i}_{org_id[:8]}@acrevia.ag",
            hashed_password="hashed_pw_test",
            full_name=f"FPO Farmer {i}",
            phone=f"+91999900000{i}",
            language_preference="te",
        )
        db_session.add(dummy_user)
        db_session.flush()

        from backend.app.models.collective import OrganizationMembership
        membership = OrganizationMembership(
            organization_id=org_id,
            user_id=dummy_user.id,
            org_role="MEMBER",
            is_active=True,
        )
        db_session.add(membership)

        dummy_farm = Farm(
            owner_id=dummy_user.id,
            name=f"Member Farm {i}",
            state="Telangana",
            district="Warangal",
            mandal="Geesugonda",
            village="Dharmaram",
            total_acreage=2.5,
        )
        db_session.add(dummy_farm)
        db_session.flush()

        dummy_plot = Plot(
            farm_id=dummy_farm.id,
            name="Main Plot",
            acreage=2.5,
        )
        db_session.add(dummy_plot)
        db_session.flush()

        dummy_season = CropSeason(
            plot_id=dummy_plot.id,
            crop_id="cotton",
            season_type="KHARIF",
            sowing_date=date(2026, 6, 15),
            status="ACTIVE",
        )
        db_session.add(dummy_season)

    # Also add 1 farm for farmer_user so total is >= 5
    f1 = Farm(
        owner_id=farmer_user.id,
        name="Farmer User Farm",
        state="Telangana",
        district="Warangal",
        mandal="Geesugonda",
        village="Dharmaram",
        total_acreage=3.0,
    )
    db_session.add(f1)
    db_session.commit()

    # Query aggregate analytics with SUFFICIENT cohort (>= 5 farms)
    res_analytics_large = client.get(f"/api/v1/collectives/organizations/{org_id}/analytics", headers=farmer_headers)
    assert res_analytics_large.status_code == 200
    large_analytics = res_analytics_large.json()
    assert large_analytics["privacy_cohort_status"] == "VALID_COHORT_GE_5"
    assert large_analytics["total_member_farms"] >= 5
    assert large_analytics["aggregated_acreage"] > 0.0
    assert "cotton" in large_analytics["crop_distribution"]


def test_scenario_d_acrevia_research_hub(
    client: TestClient,
    farmer_user: User,
    farmer_token: str,
    expert_user: User,
    expert_token: str,
    second_farmer_token: str,
):
    """Scenario D: Research projects, consent lifecycle, dataset splits, and annotation disagreement tracking."""
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    expert_headers = {"Authorization": f"Bearer {expert_token}"}
    second_headers = {"Authorization": f"Bearer {second_farmer_token}"}

    # 1. Lead researcher creates research project
    project_payload = {
        "title": "Telangana Cotton Bollworm Canopy Temperature & Pest Infestation Benchmark",
        "institution_name": "PJTSAU Department of Entomology",
        "research_objectives": "Benchmarking hyperspectral and thermal leaf canopy indices against bollworm egg counts.",
        "supported_crops": ["cotton"],
        "geographic_scope": "Warangal & Khammam",
    }
    res_proj = client.post("/api/v1/research/projects", json=project_payload, headers=expert_headers)
    assert res_proj.status_code == 201
    project = res_proj.json()
    project_id = project["id"]
    assert project["title"] == project_payload["title"]

    # 2. Farmer grants purpose-specific consent
    consent_payload = {
        "consent_scope": "ANNOTATED_IMAGES",
        "consent_version": "1.0",
    }
    res_consent = client.post(
        f"/api/v1/research/projects/{project_id}/consent",
        json=consent_payload,
        headers=farmer_headers,
    )
    assert res_consent.status_code == 201
    consent_data = res_consent.json()
    consent_id = consent_data["id"]
    assert consent_data["is_active"] is True
    assert consent_data["consent_scope"] == "ANNOTATED_IMAGES"

    # 3. Farmer revokes consent
    res_revoke = client.post(f"/api/v1/research/consents/{consent_id}/revoke", headers=farmer_headers)
    assert res_revoke.status_code == 200
    assert res_revoke.json()["is_active"] is False

    # 4. Upload dataset contribution with TRAIN split
    dataset_payload = {
        "project_id": project_id,
        "dataset_name": "warangal_cotton_thermal_train_v1",
        "crop_id": "cotton",
        "sample_count": 1200,
        "data_type": "CROP_IMAGES",
        "split_type": "TRAIN",
        "storage_uri": "s3://acrevia-research-datasets/cotton/thermal_train_v1.tar.gz",
        "license": "CC_BY_4_0",
    }
    res_ds = client.post("/api/v1/research/datasets", json=dataset_payload, headers=expert_headers)
    assert res_ds.status_code == 201
    assert res_ds.json()["split_type"] == "TRAIN"

    # 5. Create an annotation task
    task_payload = {
        "project_id": project_id,
        "task_type": "SYMPTOM_ANNOTATION",
        "entity_reference_id": "IMG-COTTON-WARANGAL-9921",
    }
    res_task = client.post("/api/v1/research/annotation-tasks", json=task_payload, headers=expert_headers)
    assert res_task.status_code == 201
    task_id = res_task.json()["id"]

    # 6. Annotator 1 submits label
    rec1_payload = {
        "label_taxonomy_version": "ACREVIA_TAXONOMY_V1",
        "label_assigned": "COTTON_BOLLWORM_DAMAGE",
        "confidence_score": "0.9500",
        "notes": "Clear rosette flower symptoms with small entry holes.",
    }
    res_rec1 = client.post(
        f"/api/v1/research/annotation-tasks/{task_id}/records",
        json=rec1_payload,
        headers=expert_headers,
    )
    assert res_rec1.status_code == 201
    assert res_rec1.json()["disagreement_flag"] is False

    # 7. Annotator 2 submits a conflicting label -> disagreement detected!
    rec2_payload = {
        "label_taxonomy_version": "ACREVIA_TAXONOMY_V1",
        "label_assigned": "TOBACCO_CATERPILLAR_DAMAGE",
        "confidence_score": "0.8000",
        "notes": "Leaf skeletonization present near lower nodes.",
    }
    res_rec2 = client.post(
        f"/api/v1/research/annotation-tasks/{task_id}/records",
        json=rec2_payload,
        headers=second_headers,
    )
    assert res_rec2.status_code == 201
    rec2_data = res_rec2.json()
    assert rec2_data["disagreement_flag"] is True

    # Verify task status is now DISPUTED
    res_task_check = client.get(f"/api/v1/research/projects/{project_id}", headers=expert_headers)
    assert res_task_check.status_code == 200
    checked_tasks = res_task_check.json()["tasks"]
    task_match = next(t for t in checked_tasks if t["id"] == task_id)
    assert task_match["status"] == "DISPUTED"


def test_scenario_e_extension_and_regional_pulse(
    client: TestClient,
    farmer_user: User,
    farmer_token: str,
    expert_token: str,
    db_session: Session,
):
    """Scenario E: Extension educational guides, event capacity limits, regional pulse threshold (N >= 3) and outbreak claim suppression."""
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    expert_headers = {"Authorization": f"Bearer {expert_token}"}

    # 1. Extension: Publish educational crop guide
    guide_payload = {
        "title": "Management of Chilli Thrips & Mites in Telangana",
        "content_body": "Use yellow sticky traps @ 20/acre and neem oil 1500 ppm @ 5ml/litre at vegetative onset.",
        "resource_type": "CROP_GUIDE",
        "crop_id": "chilli",
        "language": "en",
    }
    res_guide = client.post("/api/v1/extension/resources", json=guide_payload, headers=expert_headers)
    assert res_guide.status_code == 201
    resource_id = res_guide.json()["id"]

    # 2. Retrieve resource and verify view count increments
    res_get1 = client.get(f"/api/v1/extension/resources/{resource_id}", headers=farmer_headers)
    assert res_get1.status_code == 200
    assert res_get1.json()["view_count"] == 1

    # 3. Submit feedback
    fb_payload = {
        "feedback_type": "HELPFUL",
        "comments": "Applied in Khammam and noticed clear reduction in leaf curling.",
    }
    res_fb = client.post(f"/api/v1/extension/resources/{resource_id}/feedback", json=fb_payload, headers=farmer_headers)
    assert res_fb.status_code == 201

    # 4. Regional Pulse: Reject signal aggregation with fewer than 3 distinct farms
    bad_signal_payload = {
        "district": "Suryapet",
        "state": "Telangana",
        "crop_id": "cotton",
        "signal_category": "OBSERVATION_SURGE",
        "signal_title": "Isolated Pest Sighting",
        "signal_summary": "Single farmer reported sucking pests.",
        "confidence_tier": "FARMER_REPORT",
        "source_observation_count": 2,
        "distinct_farms_count": 1,  # Below threshold 3
        "validation_status": "UNVALIDATED_OBSERVATION",
        "recommended_action": "Monitor fields.",
        "observed_start_date": "2026-07-01",
        "observed_end_date": "2026-07-05",
    }
    res_bad_sig = client.post("/api/v1/regional-pulse/signals", json=bad_signal_payload, headers=expert_headers)
    assert res_bad_sig.status_code == 400
    assert "distinct farms" in res_bad_sig.json()["detail"].lower()

    # Create 3 verified farms and observations in Warangal within the signal window
    from backend.app.models.observation import Observation
    f_a = Farm(owner_id=farmer_user.id, name="Farm A", state="Telangana", district="Warangal", mandal="M1", village="V1", total_acreage=2.0)
    f_b = Farm(owner_id=farmer_user.id, name="Farm B", state="Telangana", district="Warangal", mandal="M2", village="V2", total_acreage=3.0)
    f_c = Farm(owner_id=farmer_user.id, name="Farm C", state="Telangana", district="Warangal", mandal="M3", village="V3", total_acreage=4.0)
    db_session.add_all([f_a, f_b, f_c])
    db_session.flush()

    obs_a = Observation(farm_id=f_a.id, observer_id=farmer_user.id, notes="Pest sighting A", created_at=datetime(2026, 7, 12, tzinfo=timezone.utc))
    obs_b = Observation(farm_id=f_b.id, observer_id=farmer_user.id, notes="Pest sighting B", created_at=datetime(2026, 7, 12, tzinfo=timezone.utc))
    obs_c = Observation(farm_id=f_c.id, observer_id=farmer_user.id, notes="Pest sighting C", created_at=datetime(2026, 7, 12, tzinfo=timezone.utc))
    db_session.add_all([obs_a, obs_b, obs_c])
    db_session.commit()

    # 5. Regional Pulse: Valid signal aggregation with sensational panic keywords -> Outbreak Claim Suppressed
    panic_signal_payload = {
        "district": "Warangal",
        "state": "Telangana",
        "crop_id": "cotton",
        "signal_category": "PEST_INQUIRIES",
        "signal_title": "Catastrophic Pink Bollworm Outbreak in Warangal",
        "signal_summary": "Severe devastation reported across mandals threatening total crop loss and epidemic spread.",
        "confidence_tier": "FARMER_REPORT",
        "source_observation_count": 12,
        "distinct_farms_count": 5,  # >= 3
        "validation_status": "EXPERT_CONFIRMED",  # Non-official claiming confirmed
        "recommended_action": "Install pheromone traps @ 4/acre and inspect 20 green bolls per acre.",
        "observed_start_date": "2026-07-10",
        "observed_end_date": "2026-07-15",
        "evidences": [
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_a.id, "evidence_notes": "Obs A"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_b.id, "evidence_notes": "Obs B"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_c.id, "evidence_notes": "Obs C"},
        ],
    }
    res_sig = client.post("/api/v1/regional-pulse/signals", json=panic_signal_payload, headers=expert_headers)
    assert res_sig.status_code == 201
    sig_data = res_sig.json()
    assert sig_data["is_outbreak_claim_suppressed"] is True
    # Verify panic words were sanitized
    assert "outbreak" not in sig_data["signal_title"].lower()
    assert "devastation" not in sig_data["signal_summary"].lower()
    # Unverified panic report downgraded to UNVALIDATED_OBSERVATION
    assert sig_data["validation_status"] == "UNVALIDATED_OBSERVATION"


def test_stage12_security_and_privacy_boundaries(
    client: TestClient,
    farmer_user: User,
    farmer_token: str,
    second_farmer_token: str,
    db_session: Session,
):
    """Security tests: Tenant boundaries, non-member rejection, and privacy protection."""
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    outsider_headers = {"Authorization": f"Bearer {second_farmer_token}"}

    # 1. Farmer creates private FPO
    fpo_payload = {
        "name": "Khammam Chilli Spices Cooperative",
        "org_type": "COOPERATIVE",
        "district": "Khammam",
    }
    res_fpo = client.post("/api/v1/collectives/organizations", json=fpo_payload, headers=farmer_headers)
    assert res_fpo.status_code == 201
    org_id = res_fpo.json()["id"]

    # 2. Non-member attempt to view collective activities -> 403 Forbidden
    res_acts = client.get(f"/api/v1/collectives/organizations/{org_id}/activities", headers=outsider_headers)
    assert res_acts.status_code == 403
    assert "member" in res_acts.json()["detail"].lower()

    # 3. Non-member attempt to access collective analytics -> 403 Forbidden
    res_ana = client.get(f"/api/v1/collectives/organizations/{org_id}/analytics", headers=outsider_headers)
    assert res_ana.status_code == 403
    assert "member" in res_ana.json()["detail"].lower()

    # 4. Non-member attempt to create activity in private org -> 403 Forbidden
    act_payload = {
        "activity_type": "GROUP_ANNOUNCEMENT",
        "title": "Unauthorized Announcement",
        "description": "Intrusion test",
        "target_date": date.today().isoformat(),
    }
    res_bad_act = client.post(f"/api/v1/collectives/organizations/{org_id}/activities", json=act_payload, headers=outsider_headers)
    assert res_bad_act.status_code == 403
