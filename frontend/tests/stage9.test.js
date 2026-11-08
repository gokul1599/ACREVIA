import { test } from 'node:test';
import assert from 'node:assert/strict';
import { api } from '../lib/api/client.ts';
import { en } from '../messages/en.ts';
import { te } from '../messages/te.ts';
import { hi } from '../messages/hi.ts';

test('Stage 9 - Precision Agriculture API Client interface contains all required methods', () => {
  assert.strictEqual(typeof api.savePlotGeometry, 'function', 'Missing savePlotGeometry');
  assert.strictEqual(typeof api.getPlotGeometry, 'function', 'Missing getPlotGeometry');
  assert.strictEqual(typeof api.updateLocationPermission, 'function', 'Missing updateLocationPermission');
  assert.strictEqual(typeof api.getSatelliteTimeSeries, 'function', 'Missing getSatelliteTimeSeries');
  assert.strictEqual(typeof api.getLatestSatelliteObservation, 'function', 'Missing getLatestSatelliteObservation');
  assert.strictEqual(typeof api.registerSensorDevice, 'function', 'Missing registerSensorDevice');
  assert.strictEqual(typeof api.listFarmSensorDevices, 'function', 'Missing listFarmSensorDevices');
  assert.strictEqual(typeof api.getPlotSensorTelemetry, 'function', 'Missing getPlotSensorTelemetry');
  assert.strictEqual(typeof api.getPlotFusionAssessment, 'function', 'Missing getPlotFusionAssessment');
  assert.strictEqual(typeof api.recordHarvestMeasurement, 'function', 'Missing recordHarvestMeasurement');
  assert.strictEqual(typeof api.getYieldForecast, 'function', 'Missing getYieldForecast');
  assert.strictEqual(typeof api.traverseKnowledgeGraph, 'function', 'Missing traverseKnowledgeGraph');
});

test('Stage 9 - Localization parity for precision agriculture namespace across EN, TE, and HI', () => {
  assert.ok(en.precision, 'en missing precision namespace');
  assert.ok(te.precision, 'te missing precision namespace');
  assert.ok(hi.precision, 'hi missing precision namespace');

  const enKeys = Object.keys(en.precision).sort();
  const teKeys = Object.keys(te.precision).sort();
  const hiKeys = Object.keys(hi.precision).sort();

  assert.deepStrictEqual(teKeys, enKeys, 'Telugu precision keys do not match English');
  assert.deepStrictEqual(hiKeys, enKeys, 'Hindi precision keys do not match English');
});

test('Stage 9 - Non-negotiable evidence disclaimer is preserved in all dictionaries', () => {
  assert.ok(
    en.precision.satelliteDisclaimer.toLowerCase().includes('not diagnose specific plant diseases'),
    'English disclaimer missing non-diagnosis clause'
  );
  assert.ok(
    te.precision.satelliteDisclaimer.includes('తెగుళ్లను లేదా వ్యాధులను నిర్ధారించలేవు'),
    'Telugu disclaimer missing non-diagnosis clause'
  );
  assert.ok(
    hi.precision.satelliteDisclaimer.includes('पादप रोगों या रोगाणुओं का निदान नहीं करते'),
    'Hindi disclaimer missing non-diagnosis clause'
  );
});

test('Stage 9 - Governed yield forecasting withholding notice is present in all dictionaries', () => {
  assert.ok(en.precision.yieldWithheld.length > 0, 'en missing yieldWithheld');
  assert.ok(te.precision.yieldWithheld.length > 0, 'te missing yieldWithheld');
  assert.ok(hi.precision.yieldWithheld.length > 0, 'hi missing yieldWithheld');
});
