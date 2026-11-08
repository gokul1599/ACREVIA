import test from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

test("PWA - Manifest specification and icons", () => {
  const manifestPath = path.resolve(__dirname, "../public/manifest.json");
  assert.ok(fs.existsSync(manifestPath), "manifest.json must exist in public directory");

  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
  assert.strictEqual(manifest.short_name, "ACREVIA");
  assert.strictEqual(manifest.display, "standalone");
  assert.strictEqual(manifest.theme_color, "#1E3A2B");
  assert.strictEqual(manifest.background_color, "#F7F5F0");
  assert.ok(manifest.icons.length >= 2, "Must contain at least 192px and 512px icons");

  for (const icon of manifest.icons) {
    const iconFile = path.resolve(__dirname, "../public", icon.src.replace(/^\//, ""));
    assert.ok(fs.existsSync(iconFile), `Icon file ${icon.src} must exist physically`);
  }
});

test("PWA - Service worker exists and defines offline shell strategy", () => {
  const swPath = path.resolve(__dirname, "../public/sw.js");
  assert.ok(fs.existsSync(swPath), "sw.js must exist in public directory");

  const swContent = fs.readFileSync(swPath, "utf-8");
  assert.ok(swContent.includes("CACHE_NAME"), "Must define CACHE_NAME");
  assert.ok(swContent.includes("STATIC_ASSETS"), "Must define STATIC_ASSETS");
  assert.ok(swContent.includes("fetch"), "Must intercept fetch events");
});
