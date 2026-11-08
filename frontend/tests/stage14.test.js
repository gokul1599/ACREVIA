import { test } from 'node:test';
import assert from 'node:assert/strict';
import { api } from '../lib/api/client.ts';
import { en } from '../messages/en.ts';
import { te } from '../messages/te.ts';
import { hi } from '../messages/hi.ts';

test('Stage 14 - Data Exchange, Partners, Developer, Consent & Webhooks API Client methods exist', () => {
  // Exchange
  assert.strictEqual(typeof api.requestDataExport, 'function', 'Missing requestDataExport');
  assert.strictEqual(typeof api.getDataExport, 'function', 'Missing getDataExport');
  assert.strictEqual(typeof api.requestDataImport, 'function', 'Missing requestDataImport');
  assert.strictEqual(typeof api.getDataImport, 'function', 'Missing getDataImport');
  assert.strictEqual(typeof api.createMappingProfile, 'function', 'Missing createMappingProfile');
  assert.strictEqual(typeof api.listMappingProfiles, 'function', 'Missing listMappingProfiles');

  // Partners
  assert.strictEqual(typeof api.listPartners, 'function', 'Missing listPartners');
  assert.strictEqual(typeof api.registerPartner, 'function', 'Missing registerPartner');
  assert.strictEqual(typeof api.getPartner, 'function', 'Missing getPartner');
  assert.strictEqual(typeof api.verifyPartner, 'function', 'Missing verifyPartner');
  assert.strictEqual(typeof api.addPartnerIntegration, 'function', 'Missing addPartnerIntegration');
  assert.strictEqual(typeof api.listPartnerIntegrations, 'function', 'Missing listPartnerIntegrations');

  // Developer
  assert.strictEqual(typeof api.listDeveloperApplications, 'function', 'Missing listDeveloperApplications');
  assert.strictEqual(typeof api.createDeveloperApplication, 'function', 'Missing createDeveloperApplication');
  assert.strictEqual(typeof api.generateApiCredential, 'function', 'Missing generateApiCredential');
  assert.strictEqual(typeof api.revokeApiCredential, 'function', 'Missing revokeApiCredential');

  // Consent Grants
  assert.strictEqual(typeof api.listConsentGrants, 'function', 'Missing listConsentGrants');
  assert.strictEqual(typeof api.grantConsent, 'function', 'Missing grantConsent');
  assert.strictEqual(typeof api.revokeConsent, 'function', 'Missing revokeConsent');

  // Webhooks
  assert.strictEqual(typeof api.listWebhookEndpoints, 'function', 'Missing listWebhookEndpoints');
  assert.strictEqual(typeof api.registerWebhookEndpoint, 'function', 'Missing registerWebhookEndpoint');
  assert.strictEqual(typeof api.deactivateWebhookEndpoint, 'function', 'Missing deactivateWebhookEndpoint');
  assert.strictEqual(typeof api.listWebhookDeliveries, 'function', 'Missing listWebhookDeliveries');
  assert.strictEqual(typeof api.retryWebhookDelivery, 'function', 'Missing retryWebhookDelivery');

  // Standards
  assert.strictEqual(typeof api.convertUnit, 'function', 'Missing convertUnit');
  assert.strictEqual(typeof api.getCropTaxonomy, 'function', 'Missing getCropTaxonomy');
  assert.strictEqual(typeof api.getConnectorHealth, 'function', 'Missing getConnectorHealth');
});

test('Stage 14 - Localization parity for exchange, partners, developer, webhooks across EN, TE, and HI', () => {
  const namespaces = ['exchange', 'partners', 'developer', 'webhooks'];

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

test('Stage 14 - Conflict preservation and SHA-256 cryptographic terms present in all locales', () => {
  assert.ok(en.exchange.preserveConflicts.length > 5, 'en missing preserveConflicts');
  assert.ok(te.exchange.preserveConflicts.length > 5, 'te missing preserveConflicts');
  assert.ok(hi.exchange.preserveConflicts.length > 5, 'hi missing preserveConflicts');

  assert.ok(en.exchange.checksum.includes('SHA-256'), 'en checksum missing SHA-256');
  assert.ok(te.exchange.checksum.includes('SHA-256'), 'te checksum missing SHA-256');
  assert.ok(hi.exchange.checksum.includes('SHA-256'), 'hi checksum missing SHA-256');
});
