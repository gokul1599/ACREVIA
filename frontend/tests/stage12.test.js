import { test } from 'node:test';
import assert from 'node:assert/strict';
import { api } from '../lib/api/client.ts';
import { en } from '../messages/en.ts';
import { te } from '../messages/te.ts';
import { hi } from '../messages/hi.ts';

test('Stage 12 - Agricultural Collaboration, Commons, Collectives, Research, Extension & Regional Pulse API Client methods', () => {
  assert.strictEqual(typeof api.listCommunities, 'function', 'Missing listCommunities');
  assert.strictEqual(typeof api.joinCommunity, 'function', 'Missing joinCommunity');
  assert.strictEqual(typeof api.createCommunityPost, 'function', 'Missing createCommunityPost');
  assert.strictEqual(typeof api.listCommunityPosts, 'function', 'Missing listCommunityPosts');
  assert.strictEqual(typeof api.addCommunityComment, 'function', 'Missing addCommunityComment');
  assert.strictEqual(typeof api.votePostHelpful, 'function', 'Missing votePostHelpful');
  assert.strictEqual(typeof api.submitKnowledgeContribution, 'function', 'Missing submitKnowledgeContribution');
  assert.strictEqual(typeof api.listKnowledgeContributions, 'function', 'Missing listKnowledgeContributions');
  assert.strictEqual(typeof api.registerOrganization, 'function', 'Missing registerOrganization');
  assert.strictEqual(typeof api.listOrganizations, 'function', 'Missing listOrganizations');
  assert.strictEqual(typeof api.getCollectiveAnalytics, 'function', 'Missing getCollectiveAnalytics');
  assert.strictEqual(typeof api.listResearchProjects, 'function', 'Missing listResearchProjects');
  assert.strictEqual(typeof api.grantResearchConsent, 'function', 'Missing grantResearchConsent');
  assert.strictEqual(typeof api.listLearningResources, 'function', 'Missing listLearningResources');
  assert.strictEqual(typeof api.registerForTrainingEvent, 'function', 'Missing registerForTrainingEvent');
  assert.strictEqual(typeof api.queryRegionalSignals, 'function', 'Missing queryRegionalSignals');
});

test('Stage 12 - Localization parity for connect, commons, collectives, research, extension, regionalPulse across EN, TE, and HI', () => {
  const namespaces = ['connect', 'commons', 'collectives', 'research', 'extension', 'regionalPulse'];

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

test('Stage 12 - Essential safety disclaimers and privacy notices present in all languages', () => {
  // Connect scientific disclaimer
  assert.ok(en.connect.helpfulDisclaimer.length > 10, 'en missing helpful disclaimer');
  assert.ok(te.connect.helpfulDisclaimer.length > 10, 'te missing helpful disclaimer');
  assert.ok(hi.connect.helpfulDisclaimer.length > 10, 'hi missing helpful disclaimer');

  // Collectives privacy cohort notice (N >= 5)
  assert.ok(en.collectives.cohortPrivacyNotice.includes('5'), 'en collectives cohort notice missing 5');
  assert.ok(te.collectives.cohortPrivacyNotice.includes('5'), 'te collectives cohort notice missing 5');
  assert.ok(hi.collectives.cohortPrivacyNotice.includes('5'), 'hi collectives cohort notice missing 5');

  // Regional Pulse outbreak suppression notice
  assert.ok(en.regionalPulse.outbreakSuppressionNotice.length > 10, 'en regionalPulse outbreak suppression notice missing');
  assert.ok(te.regionalPulse.outbreakSuppressionNotice.length > 10, 'te regionalPulse outbreak suppression notice missing');
  assert.ok(hi.regionalPulse.outbreakSuppressionNotice.length > 10, 'hi regionalPulse outbreak suppression notice missing');
});
