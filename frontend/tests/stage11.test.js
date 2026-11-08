import { test } from 'node:test';
import assert from 'node:assert/strict';
import { api } from '../lib/api/client.ts';
import { en } from '../messages/en.ts';
import { te } from '../messages/te.ts';
import { hi } from '../messages/hi.ts';

test('Stage 11 - Agricultural Economics, Market, Harvest & Traceability API Client contains all required methods', () => {
  assert.strictEqual(typeof api.createExpense, 'function', 'Missing createExpense');
  assert.strictEqual(typeof api.getExpenses, 'function', 'Missing getExpenses');
  assert.strictEqual(typeof api.correctExpense, 'function', 'Missing correctExpense');
  assert.strictEqual(typeof api.createSaleTransaction, 'function', 'Missing createSaleTransaction');
  assert.strictEqual(typeof api.getSales, 'function', 'Missing getSales');
  assert.strictEqual(typeof api.getMarketPrices, 'function', 'Missing getMarketPrices');
  assert.strictEqual(typeof api.compareMarketRealizations, 'function', 'Missing compareMarketRealizations');
  assert.strictEqual(typeof api.createHarvestPlan, 'function', 'Missing createHarvestPlan');
  assert.strictEqual(typeof api.getHarvestPlans, 'function', 'Missing getHarvestPlans');
  assert.strictEqual(typeof api.createHarvestSession, 'function', 'Missing createHarvestSession');
  assert.strictEqual(typeof api.getHarvestSessions, 'function', 'Missing getHarvestSessions');
  assert.strictEqual(typeof api.recordQualityMeasurement, 'function', 'Missing recordQualityMeasurement');
  assert.strictEqual(typeof api.getLotQualityMeasurements, 'function', 'Missing getLotQualityMeasurements');
  assert.strictEqual(typeof api.createStorageLocation, 'function', 'Missing createStorageLocation');
  assert.strictEqual(typeof api.assignToStorage, 'function', 'Missing assignToStorage');
  assert.strictEqual(typeof api.getProduceLot, 'function', 'Missing getProduceLot');
  assert.strictEqual(typeof api.recordLotMovement, 'function', 'Missing recordLotMovement');
  assert.strictEqual(typeof api.verifyPublicQrCode, 'function', 'Missing verifyPublicQrCode');
  assert.strictEqual(typeof api.getSeasonEconomics, 'function', 'Missing getSeasonEconomics');
  assert.strictEqual(typeof api.createLossEvidencePackage, 'function', 'Missing createLossEvidencePackage');
});

test('Stage 11 - Localization parity for ledger, market, harvest, quality, trace, and economics namespaces across EN, TE, and HI', () => {
  const namespaces = ['ledger', 'market', 'harvest', 'quality', 'trace', 'economics'];

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

test('Stage 11 - Category key parity in ledger namespace across EN, TE, and HI', () => {
  const enCategories = Object.keys(en.ledger.categories).sort();
  const teCategories = Object.keys(te.ledger.categories).sort();
  const hiCategories = Object.keys(hi.ledger.categories).sort();

  assert.deepStrictEqual(teCategories, enCategories, 'Telugu expense categories do not match English');
  assert.deepStrictEqual(hiCategories, enCategories, 'Hindi expense categories do not match English');

  // Verify critical CACP expense categories are present
  assert.ok(enCategories.includes('SEEDS'), 'Missing SEEDS category');
  assert.ok(enCategories.includes('FERTILIZERS'), 'Missing FERTILIZERS category');
  assert.ok(enCategories.includes('LABOUR'), 'Missing LABOUR category');
  assert.ok(enCategories.includes('MACHINERY'), 'Missing MACHINERY category');
  assert.ok(enCategories.includes('TRANSPORT'), 'Missing TRANSPORT category');
});

test('Stage 11 - Traceability and market disclaimers are present across EN, TE, and HI', () => {
  assert.ok(en.market.marketDisclaimer.length > 10, 'English market disclaimer too short');
  assert.ok(te.market.marketDisclaimer.length > 10, 'Telugu market disclaimer too short');
  assert.ok(hi.market.marketDisclaimer.length > 10, 'Hindi market disclaimer too short');

  assert.ok(en.trace.privacyNotice.includes('ACREVIA Data Governance'), 'English trace privacy notice missing data governance');
  assert.ok(te.trace.privacyNotice.length > 15, 'Telugu trace privacy notice missing');
  assert.ok(hi.trace.privacyNotice.length > 15, 'Hindi trace privacy notice missing');
});
