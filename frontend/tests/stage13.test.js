import { test } from 'node:test';
import assert from 'node:assert/strict';
import { api } from '../lib/api/client.ts';
import { en } from '../messages/en.ts';
import { te } from '../messages/te.ts';
import { hi } from '../messages/hi.ts';

test('Stage 13 - Soil, Water, Climate, Nutrient, Sustain & Resilience API Client methods exist', () => {
  // Soil
  assert.strictEqual(typeof api.createSoilSample, 'function', 'Missing createSoilSample');
  assert.strictEqual(typeof api.ingestSoilLabResult, 'function', 'Missing ingestSoilLabResult');
  assert.strictEqual(typeof api.getPlotSoilHistory, 'function', 'Missing getPlotSoilHistory');

  // Water
  assert.strictEqual(typeof api.createWaterSource, 'function', 'Missing createWaterSource');
  assert.strictEqual(typeof api.listWaterSources, 'function', 'Missing listWaterSources');
  assert.strictEqual(typeof api.recordIrrigationEvent, 'function', 'Missing recordIrrigationEvent');
  assert.strictEqual(typeof api.getPlotWaterBalance, 'function', 'Missing getPlotWaterBalance');
  assert.strictEqual(typeof api.compareWaterScenarios, 'function', 'Missing compareWaterScenarios');

  // Climate
  assert.strictEqual(typeof api.getClimateBaselines, 'function', 'Missing getClimateBaselines');
  assert.strictEqual(typeof api.assessClimateExposure, 'function', 'Missing assessClimateExposure');

  // Nutrient
  assert.strictEqual(typeof api.prescribeNutrients, 'function', 'Missing prescribeNutrients');
  assert.strictEqual(typeof api.getNutrientAssessment, 'function', 'Missing getNutrientAssessment');

  // Sustain
  assert.strictEqual(typeof api.listSustainablePractices, 'function', 'Missing listSustainablePractices');
  assert.strictEqual(typeof api.recordFarmPractice, 'function', 'Missing recordFarmPractice');
  assert.strictEqual(typeof api.recordSoilCarbon, 'function', 'Missing recordSoilCarbon');
  assert.strictEqual(typeof api.getPlotEmissions, 'function', 'Missing getPlotEmissions');
  assert.strictEqual(typeof api.getPlotSustainabilityScorecard, 'function', 'Missing getPlotSustainabilityScorecard');

  // Resilience
  assert.strictEqual(typeof api.assessPlotResilience, 'function', 'Missing assessPlotResilience');
  assert.strictEqual(typeof api.getPlotResilience, 'function', 'Missing getPlotResilience');
  assert.strictEqual(typeof api.simulateResilienceAdaptation, 'function', 'Missing simulateResilienceAdaptation');
});

test('Stage 13 - Localization parity for soil, water, climate, nutrient, sustain, resilience across EN, TE, and HI', () => {
  const namespaces = ['soil', 'water', 'climate', 'nutrient', 'sustain', 'resilience'];

  for (const ns of namespaces) {
    assert.ok(en[ns], `en missing ${ns} namespace`);
    assert.ok(te[ns], `te missing ${ns} namespace`);
    assert.ok(hi[ns], `hi missing ${ns} namespace`);

    const enKeys = Object.keys(en[ns]).sort();
    const teKeys = Object.keys(te[ns]).sort();
    const hiKeys = Object.keys(hi[ns]).sort();

    assert.deepStrictEqual(teKeys, enKeys, `Telugu ${ns} keys do not match English`);
    assert.deepStrictEqual(hiKeys, enKeys, `Hindi ${ns} keys do not match English`);
  }
});

test('Stage 13 - Mandatory non-certified research disclaimer present in all languages', () => {
  assert.ok(en.sustain.disclaimer.length > 20, 'en missing sustain research disclaimer');
  assert.ok(te.sustain.disclaimer.length > 20, 'te missing sustain research disclaimer');
  assert.ok(hi.sustain.disclaimer.length > 20, 'hi missing sustain research disclaimer');
});
