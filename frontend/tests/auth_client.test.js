import { test } from 'node:test';
import assert from 'node:assert/strict';
import { resolveApiUrl, ApiError, api } from '../lib/api/client.ts';
import nextConfig from '../next.config.mjs';

test('Auth Client - resolveApiUrl handles empty base URL', () => {
  const url = resolveApiUrl('/auth/login', '');
  assert.strictEqual(url, '/api/v1/auth/login');
});

test('Auth Client - resolveApiUrl handles host without trailing slash', () => {
  const url = resolveApiUrl('/auth/login', 'http://localhost:8000');
  assert.strictEqual(url, 'http://localhost:8000/api/v1/auth/login');
});

test('Auth Client - resolveApiUrl normalizes host with trailing slash', () => {
  const url = resolveApiUrl('/auth/login', 'http://localhost:8000/');
  assert.strictEqual(url, 'http://localhost:8000/api/v1/auth/login');
});

test('Auth Client - resolveApiUrl prevents duplicate /api/v1 when base contains /api/v1', () => {
  const url = resolveApiUrl('/auth/login', 'http://localhost:8000/api/v1');
  assert.strictEqual(url, 'http://localhost:8000/api/v1/auth/login');
});

test('Auth Client - resolveApiUrl prevents duplicate /api/v1 when base contains /api/v1/', () => {
  const url = resolveApiUrl('/auth/login', 'http://localhost:8000/api/v1/');
  assert.strictEqual(url, 'http://localhost:8000/api/v1/auth/login');
});

test('Auth Client - resolveApiUrl handles production domain with /api prefix', () => {
  const url = resolveApiUrl('/auth/login', 'https://api.acrevia.in/api');
  assert.strictEqual(url, 'https://api.acrevia.in/api/v1/auth/login');
});

test('Auth Client - resolveApiUrl handles endpoint missing leading slash', () => {
  const url = resolveApiUrl('auth/login', 'http://localhost:8000');
  assert.strictEqual(url, 'http://localhost:8000/api/v1/auth/login');
});

test('Auth Client - resolveApiUrl preserves already-prefixed endpoints without duplication', () => {
  const url = resolveApiUrl('/api/v1/auth/login', 'http://localhost:8000');
  assert.strictEqual(url, 'http://localhost:8000/api/v1/auth/login');
});

test('Auth Client - next.config.mjs rewrites rule exists and targets normalized backend URL', async () => {
  assert.ok(typeof nextConfig.rewrites === 'function', 'nextConfig must define rewrites');
  const rewrites = await nextConfig.rewrites();
  assert.ok(Array.isArray(rewrites), 'rewrites must return an array');
  const v1Rewrite = rewrites.find(r => r.source === '/api/v1/:path*');
  assert.ok(v1Rewrite, 'Must contain /api/v1/:path* rewrite rule');
  assert.ok(v1Rewrite.destination.endsWith('/api/v1/:path*'), 'Destination must preserve /api/v1/:path*');
  assert.ok(!v1Rewrite.destination.includes('/api/v1/api/v1'), 'Must not produce duplicate /api/v1');
  assert.ok(!v1Rewrite.destination.includes('//api/v1'), 'Must not produce double slash');
});

test('Auth Client - ApiError stores status, detail, and correlationId', () => {
  const err = new ApiError(404, 'Endpoint unreachable', 'Route not found', 'test-cid-123');
  assert.strictEqual(err.name, 'ApiError');
  assert.strictEqual(err.status, 404);
  assert.strictEqual(err.message, 'Endpoint unreachable');
  assert.strictEqual(err.detail, 'Route not found');
  assert.strictEqual(err.correlationId, 'test-cid-123');
  assert.ok(err instanceof Error);
});

test('Auth Client - api.login function is registered and callable', () => {
  assert.strictEqual(typeof api.login, 'function');
  assert.strictEqual(typeof api.register, 'function');
  assert.strictEqual(typeof api.getCurrentUser, 'function');
});
