import { test } from 'node:test';
import assert from 'node:assert/strict';
import { api } from '../lib/api/client.ts';
import { en } from '../messages/en.ts';
import { te } from '../messages/te.ts';
import { hi } from '../messages/hi.ts';

test('Stage 10 - Digital Twin & Decision Intelligence API Client contains all required methods', () => {
  assert.strictEqual(typeof api.getFarmTwin, 'function', 'Missing getFarmTwin');
  assert.strictEqual(typeof api.getTwinCompleteness, 'function', 'Missing getTwinCompleteness');
  assert.strictEqual(typeof api.reconcileTwin, 'function', 'Missing reconcileTwin');
  assert.strictEqual(typeof api.listTwinSnapshots, 'function', 'Missing listTwinSnapshots');
  assert.strictEqual(typeof api.runSimulation, 'function', 'Missing runSimulation');
  assert.strictEqual(typeof api.getSimulation, 'function', 'Missing getSimulation');
  assert.strictEqual(typeof api.compareSimulations, 'function', 'Missing compareSimulations');
  assert.strictEqual(typeof api.solveOptimizationProblem, 'function', 'Missing solveOptimizationProblem');
  assert.strictEqual(typeof api.getOptimizationProblem, 'function', 'Missing getOptimizationProblem');
  assert.strictEqual(typeof api.listCropCalendars, 'function', 'Missing listCropCalendars');
  assert.strictEqual(typeof api.createCropTask, 'function', 'Missing createCropTask');
  assert.strictEqual(typeof api.listCropTasks, 'function', 'Missing listCropTasks');
  assert.strictEqual(typeof api.completeCropTask, 'function', 'Missing completeCropTask');
  assert.strictEqual(typeof api.analyzeDecision, 'function', 'Missing analyzeDecision');
  assert.strictEqual(typeof api.getDecisionRecord, 'function', 'Missing getDecisionRecord');
  assert.strictEqual(typeof api.recordDecisionFeedback, 'function', 'Missing recordDecisionFeedback');
});

test('Stage 10 - Localization parity for twin, simulate, optimize, plan, and decisions namespaces across EN, TE, and HI', () => {
  const namespaces = ['twin', 'simulate', 'optimize', 'plan', 'decisions'];

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

test('Stage 10 - Simulation and zero-actuation disclaimers are preserved in all languages', () => {
  // Simulation disclaimer
  assert.ok(
    en.simulate.disclaimer.toLowerCase().includes('not guaranteed yields'),
    'English simulation disclaimer missing non-guaranteed clause'
  );
  assert.ok(
    te.simulate.disclaimer.includes('హామీలు కావు'),
    'Telugu simulation disclaimer missing non-guaranteed clause'
  );
  assert.ok(
    hi.simulate.disclaimer.includes('कोई सुनिश्चित उपज गारंटी नहीं'),
    'Hindi simulation disclaimer missing non-guaranteed clause'
  );

  // Zero automated actuation disclaimer
  assert.ok(
    en.optimize.noActuationDisclaimer.toLowerCase().includes('zero automated physical actuation'),
    'English optimization disclaimer missing zero actuation clause'
  );
  assert.ok(
    te.optimize.noActuationDisclaimer.includes('ఆటోమేటిక్‌గా ఆపరేట్ చేయదు'),
    'Telugu optimization disclaimer missing zero actuation clause'
  );
  assert.ok(
    hi.optimize.noActuationDisclaimer.includes('कोई स्वचालित भौतिक संचालन नहीं'),
    'Hindi optimization disclaimer missing zero actuation clause'
  );
});
