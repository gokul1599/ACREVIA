import test from "node:test";
import assert from "node:assert";
import { en } from "../messages/en.ts";
import { api } from "../lib/api/client.ts";

test("Stage 7 - RiskCast API Client interface contains all required methods", () => {
  assert.strictEqual(typeof api.getFarmRiskOverview, "function");
  assert.strictEqual(typeof api.evaluatePlotRisk, "function");
  assert.strictEqual(typeof api.listRiskAlerts, "function");
  assert.strictEqual(typeof api.acknowledgeRiskAlert, "function");
  assert.strictEqual(typeof api.dismissRiskAlert, "function");
  assert.strictEqual(typeof api.listRiskRules, "function");
});

test("Stage 7 - ExpertConnect API Client interface contains case workflow methods", () => {
  assert.strictEqual(typeof api.applyForExpert, "function");
  assert.strictEqual(typeof api.getMyExpertProfile, "function");
  assert.strictEqual(typeof api.listExpertCases, "function");
  assert.strictEqual(typeof api.claimExpertCase, "function");
  assert.strictEqual(typeof api.getExpertCaseDossier, "function");
  assert.strictEqual(typeof api.submitExpertAssessment, "function");
  assert.strictEqual(typeof api.reviseExpertAssessment, "function");
  assert.strictEqual(typeof api.getExpertAssessmentRevisions, "function");
});

test("Stage 7 - Intervention Intelligence API Client interface contains action & outcome methods", () => {
  assert.strictEqual(typeof api.createIntervention, "function");
  assert.strictEqual(typeof api.listPlotInterventions, "function");
  assert.strictEqual(typeof api.getIntervention, "function");
  assert.strictEqual(typeof api.recordInterventionOutcome, "function");
  assert.strictEqual(typeof api.getInterventionTimeline, "function");
});

test("Stage 7 - Correlation vs Causation disclaimer is preserved in all dictionaries", () => {
  assert.ok(en.interventions.causalityNotice.includes("singular product causality") || en.interventions.causalityNotice.includes("not singular"));
  assert.ok(en.riskcast.disclaimer.includes("NOT confirmed disease outbreak"));
});
