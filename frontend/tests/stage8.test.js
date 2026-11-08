import { test } from 'node:test';
import assert from 'node:assert/strict';
import { api } from '../lib/api/client.ts';
import nextConfig from '../next.config.mjs';
import { en } from '../messages/en.ts';
import { te } from '../messages/te.ts';
import { hi } from '../messages/hi.ts';

test('Stage 8 - Next.js Production Security Headers are configured', async () => {
  assert.ok(typeof nextConfig.headers === 'function', 'nextConfig must define headers function');
  const headersList = await nextConfig.headers();
  assert.ok(Array.isArray(headersList), 'headersList must be an array');
  const catchAll = headersList.find(h => h.source === '/(.*)');
  assert.ok(catchAll, 'Catch-all security header block must exist');
  
  const headerKeys = catchAll.headers.map(h => h.key);
  assert.ok(headerKeys.includes('X-Content-Type-Options'), 'Missing X-Content-Type-Options');
  assert.ok(headerKeys.includes('X-Frame-Options'), 'Missing X-Frame-Options');
  assert.ok(headerKeys.includes('Referrer-Policy'), 'Missing Referrer-Policy');
  assert.ok(headerKeys.includes('Permissions-Policy'), 'Missing Permissions-Policy');
});

test('Stage 8 - Production API Client interface contains observability & diagnostic methods', () => {
  assert.strictEqual(typeof api.getSystemInfo, 'function');
  assert.strictEqual(typeof api.getSystemObservability, 'function');
});

test('Stage 8 - Localization parity across all three languages for core product namespaces', () => {
  const namespaces = [
    'app', 'nav', 'auth', 'onboarding', 'dashboard',
    'diagnosis', 'knowledge', 'croppulse', 'riskcast',
    'expertconnect', 'interventions', 'common'
  ];
  
  for (const ns of namespaces) {
    assert.ok(en[ns], `en missing namespace ${ns}`);
    assert.ok(te[ns], `te missing namespace ${ns}`);
    assert.ok(hi[ns], `hi missing namespace ${ns}`);
    
    const enKeys = Object.keys(en[ns]);
    const teKeys = Object.keys(te[ns]);
    const hiKeys = Object.keys(hi[ns]);
    
    assert.strictEqual(
      teKeys.length,
      enKeys.length,
      `Telugu namespace ${ns} key count (${teKeys.length}) does not match English (${enKeys.length})`
    );
    assert.strictEqual(
      hiKeys.length,
      enKeys.length,
      `Hindi namespace ${ns} key count (${hiKeys.length}) does not match English (${enKeys.length})`
    );
  }
});
