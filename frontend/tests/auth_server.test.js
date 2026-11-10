import { test } from 'node:test';
import assert from 'node:assert/strict';
import { hashPassword, verifyPassword, createAccessToken, verifyAccessToken } from '../lib/server/auth.ts';

test('Server Auth - hashPassword generates valid bcrypt hash', async () => {
  const hash = await hashPassword('kisanSecret123');
  assert.ok(hash.startsWith('$2'), 'Hash must start with bcrypt prefix ($2a or $2b)');
  assert.strictEqual(hash.length, 60, 'Bcrypt hash must be 60 characters');
});

test('Server Auth - verifyPassword validates correct credentials', async () => {
  const hash = await hashPassword('correctPassword8');
  const valid = await verifyPassword('correctPassword8', hash);
  assert.strictEqual(valid, true, 'Valid password must verify true');
});

test('Server Auth - verifyPassword rejects incorrect credentials', async () => {
  const hash = await hashPassword('correctPassword8');
  const invalid = await verifyPassword('wrongPassword8', hash);
  assert.strictEqual(invalid, false, 'Invalid password must verify false');
});

test('Server Auth - createAccessToken and verifyAccessToken work symmetrically', async () => {
  const token = await createAccessToken('usr-uuid-1234', ['FARMER'], {
    phone: '+919876543210',
    name: 'Gokul Test Farmer',
  });
  assert.ok(typeof token === 'string' && token.length > 50, 'Token must be valid JWT string');

  const payload = await verifyAccessToken(token);
  assert.ok(payload !== null, 'Payload must be decoded successfully');
  assert.strictEqual(payload.sub, 'usr-uuid-1234');
  assert.deepStrictEqual(payload.roles, ['FARMER']);
  assert.strictEqual(payload.phone, '+919876543210');
  assert.strictEqual(payload.name, 'Gokul Test Farmer');
  assert.strictEqual(payload.iss, 'acrevia-auth-service');
});
