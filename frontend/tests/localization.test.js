import test from "node:test";
import assert from "node:assert";
import { en } from "../messages/en.ts";
import { te } from "../messages/te.ts";
import { hi } from "../messages/hi.ts";

const namespaces = [
  "app",
  "nav",
  "auth",
  "onboarding",
  "dashboard",
  "diagnosis",
  "knowledge",
  "croppulse",
  "riskcast",
  "expertconnect",
  "interventions",
  "common"
];

test("Localization - English dictionary contains all core namespaces", () => {
  for (const ns of namespaces) {
    assert.ok(en[ns], `Missing namespace: ${ns} in English dictionary`);
  }
});

test("Localization - Telugu dictionary has parity with English keys", () => {
  for (const ns of namespaces) {
    assert.ok(te[ns], `Missing namespace: ${ns} in Telugu dictionary`);
    for (const key of Object.keys(en[ns])) {
      assert.ok(te[ns][key], `Missing Telugu key: ${ns}.${key}`);
    }
  }
});

test("Localization - Hindi dictionary has parity with English keys", () => {
  for (const ns of namespaces) {
    assert.ok(hi[ns], `Missing namespace: ${ns} in Hindi dictionary`);
    for (const key of Object.keys(en[ns])) {
      assert.ok(hi[ns][key], `Missing Hindi key: ${ns}.${key}`);
    }
  }
});
